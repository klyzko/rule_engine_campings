from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from domain.entities.rule_log_ent import RuleLog as RuleLogEntity
from domain.repositories.irule_log_crud import IRuleLogRepository
from infrastructure.model.rule_log_db import RuleLog
from datetime import datetime

class SQLAlchemyRuleLogRepository(IRuleLogRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, log: RuleLogEntity) -> RuleLogEntity:
        """Создание записи лога"""
        db_log = RuleLog(
            campaign_id=log.campaign_id,
            triggered_rule=log.triggered_rule,
            previous_target=log.previous_target.value if log.previous_target else None,
            new_target=log.new_target.value if log.new_target else None,
            context=log.context,
            created_at=datetime.utcnow()
        )

        self.session.add(db_log)
        await self.session.commit()
        await self.session.refresh(db_log)

        return self._model_to_entity(db_log)

    async def get_by_campaign_id(self, campaign_id: UUID, limit: int = 10, offset: int = 0) -> Tuple[
        List[RuleLogEntity], int]:
        """Получение истории по кампании с пагинацией (от новых к старым)"""
        # Получаем общее количество записей
        count_query = select(func.count()).select_from(RuleLog).where(RuleLog.campaign_id == campaign_id)
        total = await self.session.scalar(count_query)

        # Получаем данные с пагинацией (от новых к старым)
        query = (
            select(RuleLog)
            .where(RuleLog.campaign_id == campaign_id)
            .order_by(desc(RuleLog.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        db_logs = result.scalars().all()

        logs = [self._model_to_entity(db_log) for db_log in db_logs]
        return logs, total or 0

    @staticmethod
    def _model_to_entity(model: RuleLog) -> RuleLogEntity:
        """Конвертация ORM модели в domain entity"""
        from domain.entities.company_ent import CampaignStatus

        return RuleLogEntity(
            id=model.id,
            campaign_id=model.campaign_id,
            triggered_rule=model.triggered_rule,
            previous_target=CampaignStatus(model.previous_target) if model.previous_target else None,
            new_target=CampaignStatus(model.new_target) if model.new_target else None,
            context=model.context,
            created_at=model.created_at
        )