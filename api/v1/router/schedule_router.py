from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from api.v1.shemas.schedule_shemas import ScheduleCreate, ScheduleResponse,ScheduleList
from core.depend_pg import get_db
from infrastructure.repositories.shedule_crud_orm import SQLAlchemyScheduleRepository
from domain.repositories.ischedule_crud import IScheduleRepository
from domain.entities.shedule_ent import Shedule
from application.shedule import shedule_logik
from collections import defaultdict

router = APIRouter(prefix="/{id}/schedules", tags=["schedule"])
def merge_intervals_with_validation(intervals: List[ScheduleCreate]) -> List[ScheduleCreate]:
    """
    Объединяет интервалы, проверяя что они в одном дне и у одной кампании.
    """
    if not intervals:
        return intervals

    # Проверяем что все интервалы для одной кампании
    campaign_ids = set(i.campaign_id for i in intervals)
    if len(campaign_ids) > 1:
        raise ValueError("All intervals must belong to the same campaign")

    campaign_id = next(iter(campaign_ids))

    # Группируем по дням
    by_day = defaultdict(list)
    for interval in intervals:
        by_day[interval.day_of_week].append(interval)

    merged_result = []

    for day, day_intervals in by_day.items():
        # Сортируем по времени
        sorted_intervals = sorted(day_intervals, key=lambda x: x.start_time.time())

        merged = []
        current = sorted_intervals[0]

        for next_interval in sorted_intervals[1:]:
            # Проверяем перекрытие или соприкосновение
            if current.end_time.time() >= next_interval.start_time.time():
                # Объединяем
                merged_start = min(current.start_time, next_interval.start_time)
                merged_end = max(current.end_time, next_interval.end_time)

                current = ScheduleResponse(
                    id=None,
                    campaign_id=campaign_id,
                    day_of_week=day,
                    start_time=merged_start,
                    end_time=merged_end
                )
            else:
                merged.append(current)
                current = next_interval

        merged.append(current)
        merged_result.extend(merged)

    return merged_result

@router.put("/",  status_code=status.HTTP_201_CREATED)
async def create_schedule(
    sched: ScheduleList,
    id_company:UUID,
    session: AsyncSession = Depends(get_db)
):
    """Создание нового слота расписания"""
    shedul_taske =merge_intervals_with_validation( sched.data)
    db=SQLAlchemyScheduleRepository(session)
    logik = shedule_logik(db)
    try:
        res = await logik.put(shedul_taske)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return res


@router.get("/")
async def get_schedules(
    id_company:UUID,
    session: AsyncSession = Depends(get_db)
 ):
    db=SQLAlchemyScheduleRepository(session)
    res=await db.get_by_campaign_id(id_company)
    return res


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
        id_company: UUID,
        session: AsyncSession = Depends(get_db)
 ):
    db=SQLAlchemyScheduleRepository(session)
    deleted = await db.delete(id_company)
    if not deleted:
         raise HTTPException(status_code=404, detail="Schedule not found")
    return deleted
