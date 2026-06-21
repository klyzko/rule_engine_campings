from abc import ABC, abstractmethod
from domain.entities.company_ent import Company, CampaignStatus
from domain.entities.shedule_ent import Shedule
from domain.repositories.icompany_crud import ICampaignRepository
from domain.repositories.ischedule_crud import IScheduleRepository
from infrastructure.repositories.rule_log_repository import SQLAlchemyRuleLogRepository
from domain.entities.rule_log_ent import RuleLog
from uuid import UUID
from datetime import datetime
from typing import List, Optional, Dict, Any
import json
from decimal import Decimal


def json_serializable(obj: Any) -> Any:
    """Преобразует объекты Decimal в float для JSON сериализации"""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {key: json_serializable(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [json_serializable(item) for item in obj]
    return obj


class CampaignRule(ABC):
    @abstractmethod
    def evaluate(self, campaign: Company, schedules: List[Shedule] = None) -> tuple[str | None, str | None, str | None]:
        """
        Возвращает (статус, название_правила, детали)
        """
        pass


class ScheduleRule(CampaignRule):
    def evaluate(self, campaign: Company, schedules: List[Shedule] = None) -> tuple[str | None, str | None, str | None]:
        if not campaign.schedule_enabled:
            return None, None, None

        if not schedules:
            return "paused", "schedule", "Нет активных слотов расписания"

        now = datetime.now().time()
        current_day = datetime.now().weekday()

        for slot in schedules:
            if slot.day_of_week == current_day:
                if slot.start_time <= now <= slot.end_time:
                    return None, None, None

        return "paused", "schedule", f"Текущее время {now.strftime('%H:%M')} вне активного окна"


class StockRule(CampaignRule):
    def evaluate(self, campaign: Company, schedules: List[Shedule] = None) -> tuple[str | None, str | None, str | None]:
        if campaign.stock_days_min is None:
            return None, None, None

        if campaign.stock_days_left < campaign.stock_days_min:
            return "paused", "stock", f"Остаток {campaign.stock_days_left} дней < минимума {campaign.stock_days_min}"

        return None, None, None


class BudgetRule(CampaignRule):
    def evaluate(self, campaign: Company, schedules: List[Shedule] = None) -> tuple[str | None, str | None, str | None]:
        if campaign.budget_limit is None:
            return None, None, None

        if campaign.spend_today >= campaign.budget_limit:
            return "paused", "budget", f"Потрачено {campaign.spend_today} >= лимита {campaign.budget_limit}"

        return None, None, None


class CampaignEvaluator:
    def __init__(self):
        self._rules = [
            ScheduleRule(),
            StockRule(),
            BudgetRule(),
        ]

    def evaluate(self, campaign: Company, schedules: List[Shedule] = None) -> Dict[str, Any]:
        for rule in self._rules:
            status, rule_name, details = rule.evaluate(campaign, schedules)
            if status is not None:
                return {
                    "target_status": status,
                    "triggered_rule": rule_name,
                    "rule_details": details
                }

        return {
            "target_status": "active",
            "triggered_rule": None,
            "rule_details": "Нет ограничений"
        }


class EvaluateCampaignUseCase:
    def __init__(self, evaluator: CampaignEvaluator, campaign_repo: ICampaignRepository,
                 schedule_repo: IScheduleRepository, log_repo: SQLAlchemyRuleLogRepository):
        self._evaluator = evaluator
        self._campaign_repo = campaign_repo
        self._schedule_repo = schedule_repo
        self._log_repo = log_repo

    async def execute(self, id_company: UUID) -> Dict[str, Any]:
        campaign = await self._campaign_repo.get_by_id(id_company)
        previous_target = campaign.target_status

        # Формируем контекст с преобразованием Decimal
        context = json_serializable({
            "is_managed": campaign.is_managed,
            "current_status": campaign.current_status.value if campaign.current_status else None,
            "spend_today": campaign.spend_today,
            "budget_limit": campaign.budget_limit,
            "stock_days_left": campaign.stock_days_left,
            "stock_days_min": campaign.stock_days_min,
            "schedule_enabled": campaign.schedule_enabled
        })

        if not campaign.is_managed:
            result = {
                "target_status": campaign.target_status.value if campaign.target_status else None,
                "triggered_rule": "management_disabled",
                "rule_details": "Управление выключено, статус не меняется"
            }

            # Логируем
            await self._log_repo.create(RuleLog(
                campaign_id=id_company,
                triggered_rule="management_disabled",
                previous_target=previous_target,
                new_target=campaign.target_status,
                context=context
            ))
            return result

        schedules = await self._schedule_repo.get_by_campaign_id(id_company)
        result = self._evaluator.evaluate(campaign, schedules)

        # Обновляем target_status в БД - конвертируем строку в Enum
        new_status = CampaignStatus(result["target_status"].upper())
        campaign.target_status = new_status
        await self._campaign_repo.update(campaign)

        # Добавляем rule_details в контекст
        context["rule_details"] = result["rule_details"]

        # Логируем
        await self._log_repo.create(RuleLog(
            campaign_id=id_company,
            triggered_rule=result["triggered_rule"],
            previous_target=previous_target,
            new_target=new_status,
            context=context
        ))

        return result


class EvaluateAllCampaignsUseCase:
    def __init__(self, campaign_repo: ICampaignRepository, schedule_repo: IScheduleRepository,
                 log_repo: SQLAlchemyRuleLogRepository):
        self._campaign_repo = campaign_repo
        self._schedule_repo = schedule_repo
        self._log_repo = log_repo
        self._evaluator = CampaignEvaluator()

    async def execute(self) -> Dict[str, Any]:
        campaigns = await self._campaign_repo.get_by_is_is_managed_true()
        results = []

        for campaign in campaigns:
            previous_target = campaign.target_status

            # Формируем контекст с преобразованием Decimal
            context = json_serializable({
                "is_managed": campaign.is_managed,
                "current_status": campaign.current_status.value if campaign.current_status else None,
                "spend_today": campaign.spend_today,
                "budget_limit": campaign.budget_limit,
                "stock_days_left": campaign.stock_days_left,
                "stock_days_min": campaign.stock_days_min,
                "schedule_enabled": campaign.schedule_enabled
            })

            schedules = await self._schedule_repo.get_by_campaign_id(campaign.id)
            result = self._evaluator.evaluate(campaign, schedules)

            # Обновляем target_status в БД - конвертируем строку в Enum
            new_status = CampaignStatus(result["target_status"].upper())
            campaign.target_status = new_status
            await self._campaign_repo.update(campaign)

            # Добавляем rule_details в контекст
            context["rule_details"] = result["rule_details"]

            # Логируем
            await self._log_repo.create(RuleLog(
                campaign_id=campaign.id,
                triggered_rule=result["triggered_rule"],
                previous_target=previous_target,
                new_target=new_status,
                context=context
            ))

            results.append({
                "campaign_id": str(campaign.id),
                "target_status": result["target_status"],
                "triggered_rule": result["triggered_rule"]
            })

        return {
            "evaluated": len(results),
            "results": results
        }