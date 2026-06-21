from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from domain.entities.shedule_ent import Shedule
from domain.repositories.ischedule_crud import IScheduleRepository
from infrastructure.model.campaign_shedules import CampaignSchedule


class SQLAlchemyScheduleRepository(IScheduleRepository):
    """Реализация репозитория расписания с SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, schedule: Shedule) -> Shedule:
        """Создание слота расписания"""
        db_schedule = CampaignSchedule(
            campaign_id=schedule.campaign_id,
            day_of_week=schedule.day_of_week,
            start_time=schedule.start_time,
            end_time=schedule.end_time
        )

        self.session.add(db_schedule)
        await self.session.commit()
        await self.session.refresh(db_schedule)

        return self._model_to_entity(db_schedule)

    async def get_by_campaign_id(self, campaign_id: UUID) -> List[Shedule]:
        """Получение всего расписания по ID кампании"""
        query = (
            select(CampaignSchedule)
            .where(CampaignSchedule.campaign_id == campaign_id)
            .order_by(CampaignSchedule.day_of_week, CampaignSchedule.start_time)
        )
        result = await self.session.execute(query)
        db_schedules = result.scalars().all()

        return [self._model_to_entity(db_schedule) for db_schedule in db_schedules]


    async def delete(self, schedule_id: UUID) -> bool:
        """Удаление слота расписания"""
        query = select(CampaignSchedule).where(CampaignSchedule.campaign_id == schedule_id)
        result = await self.session.execute(query)
        db_schedule = result.scalars().all()

        if not db_schedule:
            return False

        for schedule in db_schedule:
            await self.session.delete(schedule)
        await self.session.commit()
        return True

    @staticmethod
    def _model_to_entity(model: CampaignSchedule) -> Shedule:
        """Конвертация ORM модели в domain entity"""
        return Shedule(
            id=model.id,
            campaign_id=model.campaign_id,
            day_of_week=model.day_of_week,
            start_time=model.start_time,
            end_time=model.end_time
        )