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
class Company:
    id:UUID|None
    name:str|None
    current_status:CampaignStatus|None
    target_status:CampaignStatus|None
    is_managed:bool|None
    budget_limit:int|None
    spend_today:bool|None
    stock_days_left:int|None
    stock_days_min:int|None
    schedule_enabled:bool|None
    created_at:datetime|None
    updated_at:datetime|None
