from fastapi import APIRouter, Query
from typing import List, Optional
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Thống kê & Aggregation (Analytics)"])

@router.get("/by-department", response_model=List[dict])
def get_department_stats(year: Optional[int] = Query(None, description="Lọc theo năm khám")):
    """
    Thống kê số lượng ca khám và bác sĩ theo từng chuyên khoa.
    """
    return AnalyticsService.get_department_stats(year=year)

@router.get("/by-age-group", response_model=List[dict])
def get_age_group_distribution():
    """
    Thống kê phân bổ bệnh theo các nhóm tuổi (Nhi, Thanh niên, Trung niên, Cao tuổi).
    """
    return AnalyticsService.get_age_group_distribution()

@router.get("/revisit-rate", response_model=dict)
def get_revisit_statistics():
    """
    Thống kê tần suất và tỷ lệ tái khám của bệnh nhân trong phòng khám.
    """
    return AnalyticsService.get_revisit_statistics()
