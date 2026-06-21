# domain/repositories/schedule_repository.py
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from domain.entities.shedule_ent import Shedule


class IScheduleRepository(ABC):
    """Интерфейс репозитория расписания"""
    @abstractmethod
    async def get_by_campaign_id(self, campaign_id: UUID) -> List[Shedule]:
        """Получение всего расписания по ID кампании"""
        pass

    @abstractmethod
    async def create(self, schedule: Shedule) -> Shedule:
        """Создание нового расписания"""
        pass

    @abstractmethod
    async def delete(self, schedule_id: UUID) -> bool:
        """Удаление слота расписания"""
        pass