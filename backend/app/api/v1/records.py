from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
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
    # Kiểm tra xem bệnh nhân có tồn tại hay không
    patient = PatientService.get_patient_by_id(data.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bệnh nhân ID '{data.patient_id}' không tồn tại. Vui lòng tạo bệnh nhân trước."
        )
    return RecordService.create_record(data)

@router.get("", response_model=dict)
def get_medical_records(
    patient_id: Optional[str] = Query(None, description="Lọc theo ID bệnh nhân"),
    department: Optional[DepartmentEnum] = Query(None, description="Lọc theo chuyên khoa"),
    skip: int = Query(0, ge=0, description="Số lượng bản ghi bỏ qua"),
    limit: int = Query(50, ge=1, le=100, description="Số lượng bản ghi tối đa")
):
    dept_val = department.value if department else None
    items, total = RecordService.list_records(
        patient_id=patient_id,
        department=dept_val,
        skip=skip,
        limit=limit
    )
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items
    }

@router.get("/{record_id}", response_model=MedicalRecordOut)
def get_medical_record(record_id: str):
    record = RecordService.get_record_by_id(record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bệnh án có ID '{record_id}'."
        )
    return record

@router.put("/{record_id}", response_model=MedicalRecordOut)
def update_medical_record(record_id: str, data: MedicalRecordUpdate):
    updated = RecordService.update_record(record_id, data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bệnh án có ID '{record_id}' để cập nhật."
        )
    return updated

@router.delete("/{record_id}", status_code=status.HTTP_200_OK)
def delete_medical_record(record_id: str):
    success = RecordService.delete_record(record_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bệnh án có ID '{record_id}' để xóa."
        )
    return {"message": "Xóa bệnh án thành công", "record_id": record_id}
