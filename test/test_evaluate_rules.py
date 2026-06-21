import pytest
from datetime import datetime, time
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal

from domain.entities.company_ent import Company, CampaignStatus
from domain.entities.shedule_ent import Shedule
from application.evaluate import (
    ScheduleRule,
    StockRule,
    BudgetRule,
    CampaignEvaluator,
    EvaluateCampaignUseCase,
    EvaluateAllCampaignsUseCase,
    json_serializable
)


class TestScheduleRule:
    """Тесты для правила расписания"""

    def test_schedule_disabled_returns_none(self):
        """Тест: если расписание выключено - правило не срабатывает"""
        campaign = Company(
            name="Test",
            current_status=CampaignStatus.ACTIVE,
            is_managed=True,
            budget_limit=None,
            spend_today=0,
            stock_days_left=10,
            stock_days_min=None,
            schedule_enabled=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        rule = ScheduleRule()
        status, rule_name, details = rule.evaluate(campaign, [])

        assert status is None
        assert rule_name is None
        assert details is None

    def test_schedule_enabled_no_slots_returns_paused(self):
        """Тест: расписание включено, но нет слотов - статус paused"""
        campaign = Company(
            name="Test",
            current_status=CampaignStatus.ACTIVE,
            is_managed=True,
            budget_limit=None,
            spend_today=0,
            stock_days_left=10,
            stock_days_min=None,
            schedule_enabled=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        rule = ScheduleRule()
        status, rule_name, details = rule.evaluate(campaign, [])

        assert status == "paused"
        assert rule_name == "schedule"
        assert "Нет активных слотов" in details

    def test_schedule_enabled_outside_slots_returns_paused(self):
        """Тест: расписание включено, текущее время вне слотов - статус paused"""
        campaign = Company(
            name="Test",
            current_status=CampaignStatus.ACTIVE,
            is_managed=True,
            budget_limit=None,
            spend_today=0,
            stock_days_left=10,
            stock_days_min=None,
            schedule_enabled=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Создаем слот с 09:00 до 21:00
        schedule = Shedule(
            campaign_id=uuid4(),
            day_of_week=datetime.now().weekday(),
            start_time=datetime.strptime("09:00", "%H:%M").time(),
            end_time=datetime.strptime("21:00", "%H:%M").time()
        )

        # Патчим datetime.now() для возврата 22:30
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr('datetime.datetime', 'now', lambda: datetime(2026, 6, 21, 22, 30, 0))

            rule = ScheduleRule()
            status, rule_name, details = rule.evaluate(campaign, [schedule])

            assert status == "paused"
            assert rule_name == "schedule"
            assert "22:30 вне активного окна" in details

    def test_schedule_enabled_inside_slots_returns_none(self):
        """Тест: расписание включено, текущее время внутри слота - правило не срабатывает"""
        campaign = Company(
            name="Test",
            current_status=CampaignStatus.ACTIVE,
            is_managed=True,
            budget_limit=None,
            spend_today=0,
            stock_days_left=10,
            stock_days_min=None,
            schedule_enabled=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Создаем слот с 09:00 до 21:00
        schedule = Shedule(
            campaign_id=uuid4(),
            day_of_week=datetime.now().weekday(),
            start_time=datetime.strptime("09:00", "%H:%M").time(),
            end_time=datetime.strptime("21:00", "%H:%M").time()
        )

        # Патчим datetime.now() для возврата 15:30
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr('datetime.datetime', 'now', lambda: datetime(2026, 6, 21, 15, 30, 0))

            rule = ScheduleRule()
            status, rule_name, details = rule.evaluate(campaign, [schedule])

            assert status is None
            assert rule_name is None
            assert details is None


class TestStockRule:
    """Тесты для правила остатков"""

    def test_stock_min_not_set_returns_none(self):
        """Тест: если минимум остатков не задан - правило не срабатывает"""
        campaign = Company(
            name="Test",
            current_status=CampaignStatus.ACTIVE,
            is_managed=True,
            budget_limit=None,
            spend_today=0,
            stock_days_left=3,
            stock_days_min=None,
            schedule_enabled=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        rule = StockRule()
        status, rule_name, details = rule.evaluate(campaign)

        assert status is None
        assert rule_name is None
        assert details is None

    def test_stock_below_min_returns_paused(self):
        """Тест: остаток меньше минимума - статус paused"""
        campaign = Company(
            name="Test",
            current_status=CampaignStatus.ACTIVE,
            is_managed=True,
            budget_limit=None,
            spend_today=0,
            stock_days_left=3,
            stock_days_min=5,
            schedule_enabled=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        rule = StockRule()
        status, rule_name, details = rule.evaluate(campaign)

        assert status == "paused"
        assert rule_name == "stock"
        assert "3 дней < минимума 5" in details

    def test_stock_above_min_returns_none(self):
        """Тест: остаток больше или равен минимуму - правило не срабатывает"""
        campaign = Company(
            name="Test",
            current_status=CampaignStatus.ACTIVE,
            is_managed=True,
            budget_limit=None,
            spend_today=0,
            stock_days_left=7,
            stock_days_min=5,
            schedule_enabled=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        rule = StockRule()
        status, rule_name, details = rule.evaluate(campaign)

        assert status is None
        assert rule_name is None
        assert details is None


class TestBudgetRule:
    """Тесты для правила бюджета"""

    def test_budget_limit_not_set_returns_none(self):
        """Тест: если лимит бюджета не задан - правило не срабатывает"""
        campaign = Company(
            name="Test",
            current_status=CampaignStatus.ACTIVE,
            is_managed=True,
            budget_limit=None,
            spend_today=1000,
            stock_days_left=10,
            stock_days_min=None,
            schedule_enabled=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        rule = BudgetRule()
        status, rule_name, details = rule.evaluate(campaign)

        assert status is None
        assert rule_name is None
        assert details is None

    def test_budget_exceeded_returns_paused(self):
        """Тест: расход превысил лимит - статус paused"""
        campaign = Company(
            name="Test",
            current_status=CampaignStatus.ACTIVE,
            is_managed=True,
            budget_limit=Decimal('1000.00'),
            spend_today=Decimal('1500.00'),
            stock_days_left=10,
            stock_days_min=None,
            schedule_enabled=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        rule = BudgetRule()
        status, rule_name, details = rule.evaluate(campaign)

        assert status == "paused"
        assert rule_name == "budget"
        assert "1500 >= лимита 1000" in details

    def test_budget_not_exceeded_returns_none(self):
        """Тест: расход не превысил лимит - правило не срабатывает"""
        campaign = Company(
            name="Test",
            current_status=CampaignStatus.ACTIVE,
            is_managed=True,
            budget_limit=Decimal('1000.00'),
            spend_today=Decimal('500.00'),
            stock_days_left=10,
            stock_days_min=None,
            schedule_enabled=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        rule = BudgetRule()
        status, rule_name, details = rule.evaluate(campaign)

        assert status is None
        assert rule_name is None
        assert details is None


class TestCampaignEvaluator:
    """Тесты для общего evaluator'а"""

    def test_priority_schedule_over_budget(self):
        """Тест: приоритет расписания выше бюджета (Пример 4)"""
        campaign = Company(
            name="Test",
            current_status=CampaignStatus.ACTIVE,
            is_managed=True,
            budget_limit=Decimal('1000.00'),
            spend_today=Decimal('1500.00'),  # Превышен бюджет
            stock_days_left=10,
            stock_days_min=None,
            schedule_enabled=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Создаем слот с 09:00 до 21:00
        schedule = Shedule(
            campaign_id=uuid4(),
            day_of_week=datetime.now().weekday(),
            start_time=datetime.strptime("09:00", "%H:%M").time(),
            end_time=datetime.strptime("21:00", "%H:%M").time()
        )

        # Патчим datetime.now() для возврата 22:30 (вне расписания)
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr('datetime.datetime', 'now', lambda: datetime(2026, 6, 21, 22, 30, 0))

            evaluator = CampaignEvaluator()
            result = evaluator.evaluate(campaign, [schedule])

            # Должен сработать schedule, а не budget (приоритет)
            assert result["target_status"] == "paused"
            assert result["triggered_rule"] == "schedule"

    def test_all_rules_ok_returns_active(self):
        """Тест: все правила в норме - статус active (Пример 5)"""
        campaign = Company(
            name="Test",
            current_status=CampaignStatus.ACTIVE,
            is_managed=True,
            budget_limit=Decimal('1000.00'),
            spend_today=Decimal('500.00'),
            stock_days_left=10,
            stock_days_min=5,
            schedule_enabled=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        evaluator = CampaignEvaluator()
        result = evaluator.evaluate(campaign, [])

        assert result["target_status"] == "active"
        assert result["triggered_rule"] is None
        assert result["rule_details"] == "Нет ограничений"

    def test_is_managed_false_returns_target_status(self):
        """Тест: если управление выключено - статус не меняется"""
        campaign = Company(
            id=uuid4(),
            name="Test",
            current_status=CampaignStatus.ACTIVE,
            target_status=CampaignStatus.PAUSED,
            is_managed=False,
            budget_limit=Decimal('1000.00'),
            spend_today=Decimal('1500.00'),
            stock_days_left=3,
            stock_days_min=5,
            schedule_enabled=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        campaign_repo = AsyncMock()
        schedule_repo = AsyncMock()
        log_repo = AsyncMock()

        campaign_repo.get_by_id = AsyncMock(return_value=campaign)
        campaign_repo.update = AsyncMock(return_value=campaign)

        evaluator = CampaignEvaluator()
        use_case = EvaluateCampaignUseCase(evaluator, campaign_repo, schedule_repo, log_repo)

        result = use_case.execute(campaign.id)

        # Пропускаем через asyncio
        import asyncio
        result = asyncio.run(result)

        assert result["target_status"] == "PAUSED"
        assert result["triggered_rule"] == "management_disabled"


class TestJsonSerializable:
    """Тесты для функции json_serializable"""

    def test_decimal_to_float(self):
        """Тест: преобразование Decimal в float"""
        decimal_value = Decimal('10.50')
        result = json_serializable(decimal_value)
        assert result == 10.5
        assert isinstance(result, float)

    def test_dict_with_decimal(self):
        """Тест: преобразование словаря с Decimal"""
        data = {
            "budget_limit": Decimal('1000.00'),
            "spend_today": Decimal('500.50')
        }
        result = json_serializable(data)
        assert result["budget_limit"] == 1000.0
        assert result["spend_today"] == 500.5

    def test_list_with_decimal(self):
        """Тест: преобразование списка с Decimal"""
        data = [Decimal('10.00'), Decimal('20.50')]
        result = json_serializable(data)
        assert result == [10.0, 20.5]

    def test_non_decimal_values_unchanged(self):
        """Тест: значения без Decimal остаются без изменений"""
        data = {
            "name": "test",
            "count": 5,
            "flag": True
        }
        result = json_serializable(data)
        assert result == data


class TestEvaluateAllCampaigns:
    """Тесты для массовой оценки кампаний"""

    def test_evaluate_all_managed_campaigns(self):
        """Тест: оценка всех управляемых кампаний"""
        campaign1 = Company(
            id=uuid4(),
            name="Test1",
            current_status=CampaignStatus.ACTIVE,
            target_status=CampaignStatus.ACTIVE,
            is_managed=True,
            budget_limit=Decimal('1000.00'),
            spend_today=Decimal('1500.00'),
            stock_days_left=10,
            stock_days_min=None,
            schedule_enabled=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        campaign2 = Company(
            id=uuid4(),
            name="Test2",
            current_status=CampaignStatus.ACTIVE,
            target_status=CampaignStatus.ACTIVE,
            is_managed=True,
            budget_limit=None,
            spend_today=0,
            stock_days_left=10,
            stock_days_min=None,
            schedule_enabled=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        campaign_repo = AsyncMock()
        schedule_repo = AsyncMock()
        log_repo = AsyncMock()

        campaign_repo.get_by_is_is_managed_true = AsyncMock(return_value=[campaign1, campaign2])
        campaign_repo.update = AsyncMock(return_value=campaign1)
        schedule_repo.get_by_campaign_id = AsyncMock(return_value=[])

        use_case = EvaluateAllCampaignsUseCase(campaign_repo, schedule_repo, log_repo)

        import asyncio
        result = asyncio.run(use_case.execute())

        assert result["evaluated"] == 2
        assert len(result["results"]) == 2
        assert result["results"][0]["triggered_rule"] == "budget"
        assert result["results"][1]["triggered_rule"] is None