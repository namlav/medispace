from fastapi import APIRouter, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from typing import List, Optional
from bson import ObjectId  # Bắt buộc import ObjectId
from pymongo.errors import DuplicateKeyError

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
    try:
        created = PatientService.create_patient(data)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã bệnh nhân '{data.patient_code}' đã tồn tại trong hệ thống."
        ) from None
    # Thêm custom_encoder để parse ObjectId
    return jsonable_encoder(created, custom_encoder={ObjectId: str})

@router.get("", response_model=dict)
def get_patients(
    skip: int = Query(0, ge=0, description="Số lượng bản ghi bỏ qua"),
    limit: int = Query(50, ge=1, le=10000, description="Số lượng bản ghi tối đa"), 
    search: Optional[str] = Query(None, description="Tìm kiếm theo Tên, Mã BN, hoặc SĐT")
):
    items, total = PatientService.list_patients(
        skip=skip, limit=limit, search=search.strip() if search else None
    )
    # Thêm custom_encoder để parse ObjectId trong list
    return jsonable_encoder({
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items
    }, custom_encoder={ObjectId: str})

@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: str):
    patient = PatientService.get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bệnh nhân có ID '{patient_id}'."
        )
    return jsonable_encoder(patient, custom_encoder={ObjectId: str})

@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(patient_id: str, data: PatientUpdate):
    if data.patient_code:
        existing = PatientService.get_patient_by_code(data.patient_code)
        if existing and existing["id"] != patient_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Mã bệnh nhân '{data.patient_code}' đã tồn tại trong hệ thống."
            )
    try:
        updated = PatientService.update_patient(patient_id, data)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã bệnh nhân '{data.patient_code}' đã tồn tại trong hệ thống."
        ) from None
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bệnh nhân có ID '{patient_id}' để cập nhật."
        )
    return jsonable_encoder(updated, custom_encoder={ObjectId: str})

@router.delete("/{patient_id}", status_code=status.HTTP_200_OK)
def delete_patient(patient_id: str):
    success = PatientService.delete_patient(patient_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bệnh nhân có ID '{patient_id}' để xóa."
        )
    return {"message": "Xóa bệnh nhân và toàn bộ bệnh án liên quan thành công", "patient_id": patient_id}