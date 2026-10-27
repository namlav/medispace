from fastapi import APIRouter, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from typing import List, Optional
from bson import ObjectId  # Bắt buộc import ObjectId
from datetime import date, datetime, time

from backend.app.models.record import (
    MedicalRecordCreate,
    MedicalRecordUpdate,
    MedicalRecordOut,
    DepartmentEnum
)
from backend.app.services.record_service import RecordService
from backend.app.services.patient_service import PatientService

router = APIRouter(prefix="/records", tags=["Bệnh án & Đơn thuốc (Medical Records)"])

@router.post("", response_model=MedicalRecordOut, status_code=status.HTTP_201_CREATED)
def create_medical_record(data: MedicalRecordCreate):
    patient = PatientService.get_patient_by_id(data.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bệnh nhân ID '{data.patient_id}' không tồn tại. Vui lòng tạo bệnh nhân trước."
        )
    created = RecordService.create_record(data)
    return jsonable_encoder(created, custom_encoder={ObjectId: str})

@router.get("", response_model=dict)
def get_medical_records(
    patient_id: Optional[str] = Query(None, description="Lọc theo ID bệnh nhân"),
    department: Optional[DepartmentEnum] = Query(None, description="Lọc theo chuyên khoa"),
    search: Optional[str] = Query(None, description="Tìm theo mã BA, bác sĩ, chẩn đoán, triệu chứng, tên/mã bệnh nhân"),
    start_date: Optional[date] = Query(None, description="Từ ngày khám (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Đến ngày khám (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0, description="Số lượng bản ghi bỏ qua"),
    limit: int = Query(50, ge=1, le=10000, description="Số lượng bản ghi tối đa") # Đã nâng le=10000
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date không được lớn hơn end_date."
        )
    dept_val = department.value if department else None
    items, total = RecordService.list_records(
        patient_id=patient_id,
        department=dept_val,
        search=search.strip() if search else None,
        start_date=datetime.combine(start_date, time.min) if start_date else None,
        end_date=datetime.combine(end_date, time.max) if end_date else None,
        skip=skip,
        limit=limit
    )
    # Thêm custom_encoder để parse ObjectId trong list
    return jsonable_encoder({
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items
    }, custom_encoder={ObjectId: str})

@router.get("/next-code", response_model=dict)
def get_next_record_code():
    code = RecordService.get_next_record_code()
    return {"next_code": code}

@router.get("/{record_id}", response_model=MedicalRecordOut)
def get_medical_record(record_id: str):
    record = RecordService.get_record_by_id(record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bệnh án có ID '{record_id}'."
        )
    return jsonable_encoder(record, custom_encoder={ObjectId: str})

@router.put("/{record_id}", response_model=MedicalRecordOut)
def update_medical_record(record_id: str, data: MedicalRecordUpdate):
    if data.patient_id is not None and not PatientService.get_patient_by_id(data.patient_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bệnh nhân ID '{data.patient_id}' không tồn tại."
        )
    updated = RecordService.update_record(record_id, data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bệnh án có ID '{record_id}' để cập nhật."
        )
    return jsonable_encoder(updated, custom_encoder={ObjectId: str})

@router.delete("/{record_id}", status_code=status.HTTP_200_OK)
def delete_medical_record(record_id: str):
    success = RecordService.delete_record(record_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bệnh án có ID '{record_id}' để xóa."
        )
    return {"message": "Xóa bệnh án thành công", "record_id": record_id}