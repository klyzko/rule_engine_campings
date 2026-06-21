from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from domain.entities.company_ent import CampaignStatus


@dataclass
class RuleLog:
    campaign_id: UUID
    triggered_rule: Optional[str]
    previous_target: Optional[CampaignStatus]
    new_target: Optional[CampaignStatus]
    context: Dict[str, Any]
    id: Optional[UUID] = None
    created_at: Optional[datetime] = None