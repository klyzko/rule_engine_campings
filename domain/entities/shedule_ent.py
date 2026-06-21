from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum
from datetime import datetime

class CampaignStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"


@dataclass
class Shedule:
    campaign_id: UUID|None
    day_of_week: int|None
    start_time: datetime|None
    end_time: datetime|None
    id: UUID | None = None