import logging
from datetime import date, datetime, time
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from pymongo.errors import PyMongoError

from backend.app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Thống kê & Aggregation (Analytics)"])


class DepartmentStat(BaseModel):
    department: str = Field(..., description="Mã chuyên khoa")
    total_cases: int = Field(..., description="Tổng số ca khám")
    revisit_cases: int = Field(..., description="Số ca có chỉ định tái khám")
    total_prescriptions: int = Field(..., description="Tổng số lượt thuốc đã kê")
    doctor_count: int = Field(..., description="Số bác sĩ khác nhau đã khám")
    total_visits: int = Field(..., description="Alias của total_cases (tương thích frontend)")
    follow_up_count: int = Field(..., description="Alias của revisit_cases (tương thích frontend)")


class AgeGroupStat(BaseModel):
    age_group: str = Field(..., description="Nhóm tuổi: 0-18, 19-40, 41-60, 60+")
    department: str = Field(..., description="Mã chuyên khoa")
    count: int = Field(..., description="Số ca bệnh trong nhóm")
    percentage: float = Field(..., description="Tỷ lệ % của chuyên khoa trong nhóm tuổi")


class RevisitLevel(BaseModel):
    level: str = Field(..., description="Mức độ tái khám")
    patient_count: int = Field(..., description="Số bệnh nhân thuộc mức độ")


class TopRevisitPatient(BaseModel):
    patient_id: str
    visit_count: int
    departments: List[str]
    latest_visit: datetime


class RevisitRateResponse(BaseModel):
    total_unique_patients: int = Field(..., description="Tổng số bệnh nhân từng đi khám")
    revisit_patients: int = Field(..., description="Bệnh nhân khám từ 2 lần trở lên")
    single_visit_patients: int = Field(..., description="Bệnh nhân chỉ khám 1 lần")
    revisit_rate_percent: float = Field(..., description="Tỷ lệ tái khám toàn viện (%)")
    distribution: List[RevisitLevel]
    top_revisit_patients: List[TopRevisitPatient]


def _raise_db_error(exc: PyMongoError) -> None:
    logger.exception("Truy vấn thống kê MongoDB thất bại")
    raise HTTPException(
        status_code=503,
        detail="Không thể truy vấn MongoDB. Vui lòng kiểm tra kết nối CSDL.",
    ) from exc


@router.get(
    "/departments",
    response_model=List[DepartmentStat],
    summary="Thống kê ca khám theo chuyên khoa",
    description="Dùng $match + $group để đếm ca khám, ca tái khám và số lượt thuốc theo từng chuyên khoa.",
)
def get_department_stats(
    start_date: Optional[date] = Query(None, description="Từ ngày (YYYY-MM-DD), tính từ 00:00"),
    end_date: Optional[date] = Query(None, description="Đến ngày (YYYY-MM-DD), tính đến 23:59:59"),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date phải trước hoặc bằng end_date.")

    start = datetime.combine(start_date, time.min) if start_date else None
    end = datetime.combine(end_date, time.max) if end_date else None
    try:
        return AnalyticsService.get_department_stats(start_date=start, end_date=end)
    except PyMongoError as exc:
        _raise_db_error(exc)


@router.get(
    "/age-groups",
    response_model=List[AgeGroupStat],
    summary="Phân bố ca bệnh theo nhóm tuổi",
    description="Dùng $lookup, $unwind, $dateDiff và $switch để phân nhóm tuổi bệnh nhân.",
)
def get_age_group_distribution():
    try:
        return AnalyticsService.get_age_group_distribution()
    except PyMongoError as exc:
        _raise_db_error(exc)


@router.get(
    "/revisit-rate",
    response_model=RevisitRateResponse,
    summary="Tỷ lệ và tần suất tái khám",
    description="Dùng $group theo patient_id và $facet + $bucket để tính tỷ lệ tái khám toàn viện.",
)
def get_revisit_rate():
    try:
        return AnalyticsService.get_revisit_rate_analysis()
    except PyMongoError as exc:
        _raise_db_error(exc)
