from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from core.depend_pg import get_db
from infrastructure.repositories.company_crud_orm import SQLAlchemyCampaignRepository
from infrastructure.repositories.shedule_crud_orm import SQLAlchemyScheduleRepository
from infrastructure.repositories.rule_log_repository import SQLAlchemyRuleLogRepository
from application.evaluate import CampaignEvaluator, EvaluateCampaignUseCase, EvaluateAllCampaignsUseCase

router = APIRouter(prefix="/campaigns", tags=["evaluate"])


@router.post("/{campaign_id}/evaluate", response_model=dict)
async def evaluate_single_campaign(
        campaign_id: UUID,
        session: AsyncSession = Depends(get_db)
):
    """Оценка одной кампании"""
    campaign_repo = SQLAlchemyCampaignRepository(session)
    schedule_repo = SQLAlchemyScheduleRepository(session)
    log_repo = SQLAlchemyRuleLogRepository(session)

    campaign = await campaign_repo.get_by_id(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    evaluator = CampaignEvaluator()
    use_case = EvaluateCampaignUseCase(evaluator, campaign_repo, schedule_repo, log_repo)
    result = await use_case.execute(campaign_id)

    return {
        "target_status": result["target_status"],
        "triggered_rule": result["triggered_rule"],
        "rule_details": result["rule_details"]
    }


@router.post("/evaluate-all", response_model=dict)
async def evaluate_all_campaigns(
        session: AsyncSession = Depends(get_db)
):
    """Оценка всех управляемых кампаний"""
    campaign_repo = SQLAlchemyCampaignRepository(session)
    schedule_repo = SQLAlchemyScheduleRepository(session)
    log_repo = SQLAlchemyRuleLogRepository(session)

    use_case = EvaluateAllCampaignsUseCase(campaign_repo, schedule_repo, log_repo)
    result = await use_case.execute()

    return result


@router.get("/{campaign_id}/evaluation-history", response_model=dict)
async def get_evaluation_history(
        campaign_id: UUID,
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        session: AsyncSession = Depends(get_db)
):
    """Получение истории вычислений для кампании (от новых к старым, с пагинацией)"""
    campaign_repo = SQLAlchemyCampaignRepository(session)

    # Проверяем существует ли кампания
    campaign = await campaign_repo.get_by_id(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    log_repo = SQLAlchemyRuleLogRepository(session)
    logs, total = await log_repo.get_by_campaign_id(campaign_id, limit=limit, offset=offset)

    return {
        "campaign_id": str(campaign_id),
        "total": total,
        "limit": limit,
        "offset": offset,
        "history": [
            {
                "id": str(log.id),
                "triggered_rule": log.triggered_rule,
                "previous_target": log.previous_target.value if log.previous_target else None,
                "new_target": log.new_target.value if log.new_target else None,
                "context": log.context,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in logs
        ]
    }