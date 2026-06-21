from datetime import time, datetime
from uuid import uuid4
from typing import Optional

from sqlalchemy import ForeignKey, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from infrastructure.model.base import Base,CampaignStatus
from sqlalchemy.orm import relationship


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
        Time(timezone=False),
        nullable=False
    )

    end_time: Mapped[time] = mapped_column(
        Time(timezone=False),
        nullable=False
    )

    campaign = relationship("Campaign", back_populates="schedules")