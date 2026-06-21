from pydantic import BaseModel, field_validator, ValidationInfo
from datetime import datetime, time
from uuid import UUID
from typing import Optional, List


class ScheduleCreate(BaseModel):
    campaign_id: UUID
    day_of_week: int  # 0-6 (Monday-Sunday)
    start_time: datetime
    end_time: datetime

    @field_validator('day_of_week')
    @classmethod
    def validate_day(cls, v: int) -> int:
        if v < 0 or v > 6:
            raise ValueError('day_of_week must be 0-6 (Monday-Sunday)')
        return v

    @field_validator('end_time')
    @classmethod
    def validate_end_after_start(cls, v: datetime, info: ValidationInfo) -> datetime:
        start = info.data.get('start_time')
        if start and v <= start:  # Используем <= чтобы запретить нулевую длительность
            raise ValueError('end_time must be after start_time')
        return v


class ScheduleResponse(BaseModel):
    id: Optional[UUID] = None
    campaign_id: UUID
    day_of_week: int
    start_time: datetime
    end_time: datetime

    model_config = {"from_attributes": True}  # В Pydantic v2 так


class ScheduleList(BaseModel):  # Исправил опечатку Shedulelist -> ScheduleList
    data: List[ScheduleResponse]

    @field_validator('data')
    @classmethod
    def validate_non_overlapping(cls, v: List[ScheduleResponse]) -> List[ScheduleResponse]:
        if not v:
            return v

        # Группируем по дню недели
        intervals_by_day = {}
        for interval in v:
            day = interval.day_of_week
            if day not in intervals_by_day:
                intervals_by_day[day] = []
            intervals_by_day[day].append(interval)

        # Проверяем перекрытия в каждом дне
        for day, intervals in intervals_by_day.items():
            # Сортируем по времени (используем только время, игнорируя дату)
            sorted_intervals = sorted(
                intervals,
                key=lambda x: x.start_time.time()  # Сортируем только по времени
            )

            for i in range(len(sorted_intervals) - 1):
                current = sorted_intervals[i]
                next_interval = sorted_intervals[i + 1]

                # Сравниваем только время
                if current.end_time.time() > next_interval.start_time.time():
                    raise ValueError(
                        f'Overlap detected on day {day} between '
                        f'{current.start_time.time()}-{current.end_time.time()} and '
                        f'{next_interval.start_time.time()}-{next_interval.end_time.time()}'
                    )
                elif current.end_time.time() == next_interval.start_time.time():
                    # Это допустимо (10:00-11:00 и 11:00-12:00)
                    pass

        return v