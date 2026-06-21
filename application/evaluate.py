from abc import ABC, abstractmethod
from domain.entities.company_ent import Company
from domain.entities.shedule_ent import Shedule
from domain.repositories.icompany_crud import ICampaignRepository
from domain.repositories.ischedule_crud import IScheduleRepository
from uuid import UUID

class CampaignRule(ABC):

    @abstractmethod
    def evaluate(self, campaign: Company) -> str | None:
        pass

class ScheduleRule(CampaignRule):

    def evaluate(self, campaign: Company) -> str | None:

        if not campaign.schedule_enabled:
            return None

        if self._outside_active_slots(campaign):
            return "paused"

        return None

    def _outside_active_slots(self, campaign: Company) -> bool:
        # логика проверки времени
        return False

class StockRule(CampaignRule):

    def evaluate(self, campaign: Company) -> str | None:

        if campaign.stock_days_min is None:
            return None

        if campaign.stock_days_left < campaign.stock_days_min:
            return "paused"

        return None

class BudgetRule(CampaignRule):

    def evaluate(self, campaign: Company) -> str | None:

        if campaign.budget_limit is None:
            return None

        if campaign.spend_today >= campaign.budget_limit:
            return "paused"

        return None

class CampaignEvaluator:

    def __init__(self):
        self._rules = [
            ScheduleRule(),
            StockRule(),
            BudgetRule(),
        ]

    def evaluate(self, campaign: Company,shedule: Shedule) -> str:

        for rule in self._rules:

            result = rule.evaluate(campaign)

            if result is not None:
                return result

        return "active"


class EvaluateCampaignUseCase:

    def __init__(self,
                 evaluator: CampaignEvaluator,
                 campaign_repo:ICampaignRepository,
                 schedule_repo:IScheduleRepository):
        self._evaluator = evaluator
        self._campaign_repo = campaign_repo
        self._schedule_repo = schedule_repo

    async def execute(self, id_company: UUID):
        campaign = await self._campaign_repo.get_by_id(id_company)
        if not campaign.is_managed:
            return campaign.target_status

        return self._evaluator.evaluate(campaign,shedule)



class EvaluateAllCampaignsUseCase:

    def __init__(
        self,
        campaign_repo,
        evaluate_campaign_use_case
    ):
        self._campaign_repo = campaign_repo
        self._evaluate_campaign = evaluate_campaign_use_case

    async def execute(self):

        campaigns = await self._campaign_repo.get_all()

        for campaign in campaigns:

            new_status = await self._evaluate_campaign.execute(
                campaign
            )

            campaign.target_status = new_status

            await self._campaign_repo.save(campaign)