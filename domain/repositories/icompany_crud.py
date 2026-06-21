# domain/repositories/campaign_repository.py
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from uuid import UUID
from domain.entities.company_ent import Company


class ICampaignRepository(ABC):
    """Интерфейс репозитория кампаний"""

    @abstractmethod
    async def create(self, campaign: Company) -> Company:
        """Создание новой кампании"""
        pass

    @abstractmethod
    async def get_by_id(self, campaign_id: UUID) -> Optional[Company]:
        """Получение кампании по ID"""
        pass

    @abstractmethod
    async def get_all(self, limit: int = 10, offset: int = 0) -> Tuple[List[Company], int]:
        """Получение списка кампаний с пагинацией"""
        pass

    @abstractmethod
    async def update(self, campaign: Company) -> Company:
        """Обновление кампании"""
        pass

    @abstractmethod
    async def delete(self, campaign_id: UUID) -> bool:
        """Удаление кампании"""
        pass
    @abstractmethod
    async def get_by_is_is_managed_true(self) -> List[Company]:
        """Получение списка управляймых кампаний"""
        pass