from datetime import time, datetime
from uuid import uuid4
from typing import Optional

from sqlalchemy import ForeignKey, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from infrastructure.model.base import Base

# Предполагаем, что Base и Campaign определены ранее
# from models import Base, Campaign

class CampaignSchedule(Base):
    __tablename__ = "campaign_schedules"

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

    day_of_week: Mapped[int] = mapped_column(
        nullable=False
    )

    start_time: Mapped[time] = mapped_column(
        Time(timezone=False),  # без таймзоны для хранения локального времени
        nullable=False
    )

    end_time: Mapped[time] = mapped_column(
        Time(timezone=False),
        nullable=False
    )

    # Уникальное ограничение: у одной кампании не может быть двух окон в один день недели
    __table_args__ = (
        UniqueConstraint('campaign_id', 'day_of_week', name='uq_campaign_day'),
        # Дополнительная проверка, что start_time < end_time (лучше на уровне приложения или триггера)
    )