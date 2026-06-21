from typing import Optional, List, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from domain.entities.company_ent import Company, CampaignStatus
from domain.repositories.icompany_crud import ICampaignRepository
from infrastructure.model.company_db import Campaign


class SQLAlchemyCampaignRepository(ICampaignRepository):
    """Реализация репозитория с SQLAlchemy ORM"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, campaign: Company) -> Company:
        """Создание новой кампании"""
        campaign.created_at = datetime.now()
        campaign.updated_at = datetime.now()
        campaign.target_status = CampaignStatus.ACTIVE
        campaign.current_status = CampaignStatus.ACTIVE
        # Конвертируем domain entity в ORM модель
        db_campaign = Campaign(
            id=campaign.id,
            name=campaign.name,
            current_status=campaign.current_status.value,
            target_status=campaign.target_status.value,
            is_managed=campaign.is_managed,
            budget_limit=campaign.budget_limit,
            spend_today=campaign.spend_today,
            stock_days_left=campaign.stock_days_left,
            stock_days_min=campaign.stock_days_min,
            schedule_enabled=campaign.schedule_enabled,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at
        )

        self.session.add(db_campaign)
        await self.session.commit()
        await self.session.refresh(db_campaign)

        return self._model_to_entity(db_campaign)

    async def get_by_id(self, campaign_id: UUID) -> Optional[Company]:
        """Получение кампании по ID"""
        query = select(Campaign).where(Campaign.id == campaign_id)
        result = await self.session.execute(query)
        db_campaign = result.scalar_one_or_none()

        if db_campaign:
            return self._model_to_entity(db_campaign)
        raise ValueError(f"Campaign with id {campaign_id} not found")

    async def get_all(self, limit: int = 10, offset: int = 0) -> Tuple[List[Company], int]:
        """Получение списка кампаний с пагинацией"""
        # Получаем общее количество записей
        count_query = select(func.count()).select_from(Campaign)
        total = await self.session.scalar(count_query)

        # Получаем данные с пагинацией
        query = (
            select(Campaign)
            .order_by(Campaign.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        db_campaigns = result.scalars().all()
        if not db_campaigns:
            raise ValueError(f"Campaigns with  not found")
        campaigns = [self._model_to_entity(db_campaign) for db_campaign in db_campaigns]
        return campaigns, total or 0

    async def update(self, campaign: Company) -> Company:
        """Обновление кампании"""
        campaign.updated_at = datetime.now()

        # Находим существующую запись
        query = select(Campaign).where(Campaign.id == campaign.id)
        result = await self.session.execute(query)
        db_campaign = result.scalar_one_or_none()

        if not db_campaign:
            raise ValueError(f"Campaign with id {campaign.id} not found")
        print(db_campaign.id)
        # Обновляем поля
        db_campaign.name = campaign.name
        db_campaign.current_status = campaign.current_status.value
        db_campaign.target_status = campaign.target_status.value
        db_campaign.is_managed = campaign.is_managed
        db_campaign.budget_limit = campaign.budget_limit
        db_campaign.spend_today = campaign.spend_today
        db_campaign.stock_days_left = campaign.stock_days_left
        db_campaign.stock_days_min = campaign.stock_days_min
        db_campaign.schedule_enabled = campaign.schedule_enabled
        db_campaign.updated_at = campaign.updated_at

        await self.session.commit()
        await self.session.refresh(db_campaign)

        return self._model_to_entity(db_campaign)

    async def delete(self, campaign_id: UUID) -> bool:
        """Удаление кампании"""
        query = select(Campaign).where(Campaign.id == campaign_id)
        result = await self.session.execute(query)
        db_campaign = result.scalar_one_or_none()

        if not db_campaign:
            return False

        await self.session.delete(db_campaign)
        await self.session.commit()
        return True

    @staticmethod
    def _model_to_entity(model: Campaign) -> Company:
        """Конвертация ORM модели в domain entity"""
        return Company(
            id=model.id,
            name=model.name,
            current_status=model.current_status,
            target_status=model.target_status,
            is_managed=model.is_managed,
            budget_limit=model.budget_limit,
            spend_today=model.spend_today,
            stock_days_left=model.stock_days_left,
            stock_days_min=model.stock_days_min,
            schedule_enabled=model.schedule_enabled,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    async def get_by_is_is_managed_true(self) -> List[Company]:
        query = select(Campaign).where(Campaign.is_managed == True)
        result = await self.session.execute(query)
        db_campaigns = result.scalars().all()
        if not db_campaigns:
            raise ValueError(f"Campaigns with  not found")
        res = [self._model_to_entity(db_campaign) for db_campaign in db_campaigns]
        return res