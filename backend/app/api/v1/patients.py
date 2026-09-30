from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from backend.app.models.patient import PatientCreate, PatientUpdate, PatientOut
from backend.app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["Bệnh nhân (Patients)"])

@router.post("", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient(data: PatientCreate):
    existing = PatientService.get_patient_by_code(data.patient_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã bệnh nhân '{data.patient_code}' đã tồn tại trong hệ thống."
        )
    return PatientService.create_patient(data)

@router.get("", response_model=dict)
def get_patients(
    skip: int = Query(0, ge=0, description="Số lượng bản ghi bỏ qua"),
    limit: int = Query(50, ge=1, le=100, description="Số lượng bản ghi tối đa"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo Tên, Mã BN, hoặc SĐT")
):
    items, total = PatientService.list_patients(skip=skip, limit=limit, search=search)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items
    }

@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: str):
    patient = PatientService.get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bệnh nhân có ID '{patient_id}'."
        )
    return patient

@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(patient_id: str, data: PatientUpdate):
    updated = PatientService.update_patient(patient_id, data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bệnh nhân có ID '{patient_id}' để cập nhật."
        )
    return updated

@router.delete("/{patient_id}", status_code=status.HTTP_200_OK)
def delete_patient(patient_id: str):
    success = PatientService.delete_patient(patient_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bệnh nhân có ID '{patient_id}' để xóa."
        )
    return {"message": "Xóa bệnh nhân thành công", "patient_id": patient_id}
