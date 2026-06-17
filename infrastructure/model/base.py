from sqlalchemy.orm import DeclarativeBase
from enum import Enum


class CampaignStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"

class Base(DeclarativeBase):
    pass