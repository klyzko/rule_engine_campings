from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from api.v1.shemas.company_shemas import Company_update
from core.depend_pg import get_db
from infrastructure.repositories.company_crud_orm import SQLAlchemyCampaignRepository
from domain.repositories.icompany_crud import ICampaignRepository
from application.evaluate import CampaignEvaluator, EvaluateCampaignUseCase, EvaluateAllCampaignsUseCase

router = APIRouter(prefix="/evaluate", tags=["evaluate"])


@router.post("/campaign/{campaign_id}", response_model=dict)
async def evaluate_single_campaign(
    campaign_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Оценка одной кампании"""
    campaign = await repo.get_by_id(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    evaluator = CampaignEvaluator()
    use_case = EvaluateCampaignUseCase(evaluator)
    new_status = await use_case.execute(campaign)

    campaign.target_status = new_status
    updated = await repo.update(campaign)

    return {
        "campaign_id": campaign.id,
        "current_status": campaign.current_status.value if campaign.current_status else None,
        "target_status": new_status
    }


# @router.post("/all-campaigns", response_model=dict)
# async def evaluate_all_campaigns(
#     repo: ICampaignRepository = Depends(get_campaign_repo)
# ):
#     """Оценка всех кампаний"""
#     evaluator = CampaignEvaluator()
#     evaluate_use_case = EvaluateCampaignUseCase(evaluator)
#     use_case = EvaluateAllCampaignsUseCase(repo, evaluate_use_case)
#
#     await use_case.execute()
#
#     return {"message": "All campaigns evaluated"}
