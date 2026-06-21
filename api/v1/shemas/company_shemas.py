from pydantic import BaseModel,field_validator,model_validator
from typing import Optional,List
from enum import Enum
from datetime import datetime
from decimal import Decimal

class status(Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"


class CompanyBase(BaseModel):
    name:str
    current_status:status=status.ACTIVE
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
    @field_validator('budget_limit','spend_today','stock_days_left','stock_days_min')
    @classmethod
    def validate_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError('value must be non-negative')
        return v
    @model_validator(mode="after")
    def validate_dates(self):
        if self.created_at > self.updated_at:
            raise ValueError(
                "created_at can be no more than updated_at"
            )
        return self


class Company_update(CompanyBase):
    id:int|None
    target_status: status

