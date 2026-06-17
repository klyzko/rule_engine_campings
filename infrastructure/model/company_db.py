from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Enum, Numeric, DateTime, Boolean, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from infrastructure.model.base import Base,CampaignStatus



# Модель таблицы
class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    name: Mapped[str] = mapped_column(nullable=False)
    current_status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus, name="campaign_status_enum"),
        nullable=False
    )
    target_status: Mapped[Optional[CampaignStatus]] = mapped_column(
        Enum(CampaignStatus, name="campaign_status_enum"),
        nullable=True
    )
    is_managed: Mapped[bool] = mapped_column(default=False)
    budget_limit: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )
    spend_today: Mapped[float] = mapped_column(
        Numeric(10, 2),
        default=0.0,
        nullable=False
    )
    stock_days_left: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    stock_days_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    schedule_enabled: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )