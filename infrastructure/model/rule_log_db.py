from datetime import datetime
from uuid import uuid4
from typing import Optional, Any, Dict
from sqlalchemy.types import JSON

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from infrastructure.model.base import Base, CampaignStatus


class RuleLog(Base):
    __tablename__ = "rule_evaluation_log"

    id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    campaign_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    triggered_rule: Mapped[Optional[str]] = mapped_column(
        nullable=True,
        comment="Какое правило сработало (null = нет ограничений)"
    )

    previous_target: Mapped[Optional[CampaignStatus]] = mapped_column(
        nullable=True
    )

    new_target: Mapped[Optional[CampaignStatus]] = mapped_column(
        nullable=True
    )

    context: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="Снапшот данных на момент вычисления"
    )

    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<RuleLog(campaign={self.campaign_id}, rule={self.triggered_rule}, {self.previous_target}->{self.new_target})>"