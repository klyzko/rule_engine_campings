from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from uuid import UUID
from domain.entities.rule_log_ent import RuleLog


class IRuleLogRepository(ABC):
    @abstractmethod
    async def create(self, log: RuleLog) -> RuleLog:
        """Создание записи лога"""
        pass

    @abstractmethod
    async def get_by_campaign_id(self, campaign_id: UUID, limit: int = 10, offset: int = 0) -> Tuple[List[RuleLog], int]:
        """Получение истории по кампании с пагинацией"""
        pass