from sqlalchemy.orm import DeclarativeBase
from enum import Enum


class CampaignStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"

class Base(DeclarativeBase):
    pass