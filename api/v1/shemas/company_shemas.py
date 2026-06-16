from pydantic import BaseModel,field_validator,model_validator
from typing import Optional
from enum import Enum
from datetime import datetime
from decimal import Decimal

class status(Enum):
       active = "active"
       paused = "paused"


class CompanyBase(BaseModel):
    name:str
    current_status:status=status.active
    #target_status:status=status.paused
    is_managed:bool = True
    budget_limit:Optional[int] = None
    spend_today:int = 0
    stock_days_left:int = 0
    stock_days_min:int = 0
    schedule_enabled:bool = True
    created_at:datetime = datetime.now()
    updated_at:datetime = datetime.now()


class Company_create(CompanyBase):
    @field_validator('budget_limit','spend_today','stock_days_left','stock_days_min',)
    @classmethod
    def validate_and_hash_password(cls, v: str) -> str:
        if v< 0:
            raise ValueError('day must be positive')
        return v
    @model_validator(mode="after")
    def validate_dates(self):
        if self.created_at > self.updated_at:
            raise ValueError(
                "created_at can be no more than updated_at"
            )
        return self


class Company_update(CompanyBase):
    id:int