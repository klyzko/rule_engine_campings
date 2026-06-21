from datetime import datetime
from uuid import uuid4
from typing import Optional, Any
from sqlalchemy.types import JSON

from sqlalchemy import ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from infrastructure.model.base import Base,CampaignStatus

# Предполагаем, что Base и CampaignStatus определены ранее
# from models import Base, CampaignStatus

class CampaignStatusHistory(Base):
    __tablename__ = "campaign_status_history"

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
        comment="Название правила, которое вызвало изменение (null = ручное изменение)"
    )

    previous_target: Mapped[Optional["CampaignStatus"]] = mapped_column(
        nullable=True
    )

    new_target: Mapped[Optional["CampaignStatus"]] = mapped_column(
        nullable=True
    )

    context: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="Снапшот данных на момент вычисления: расход, остатки и т.д."
    )

    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.utcnow  # или использовать func.now()
    )


    def __repr__(self) -> str:
        rule_info = f"rule={self.triggered_rule}" if self.triggered_rule else "manual"
        return f"<CampaignStatusHistory(campaign={self.campaign_id}, {rule_info}, {self.previous_target}->{self.new_target})>"