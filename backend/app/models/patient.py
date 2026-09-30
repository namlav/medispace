from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PatientBase(BaseModel):
    patient_code: str = Field(..., description="Mã bệnh nhân duy nhất (ví dụ: BN-1001)")
    full_name: str = Field(..., description="Họ và tên bệnh nhân")
    dob: str = Field(..., description="Ngày sinh (YYYY-MM-DD)")
    gender: str = Field(..., description="Giới tính: Nam, Nữ, Khác")
    phone: Optional[str] = Field(None, description="Số điện thoại liên hệ")
    address: Optional[str] = Field(None, description="Địa chỉ thường trú")
    blood_group: Optional[str] = Field(None, description="Nhóm máu: A, B, AB, O (+/-)")
    allergies: List[str] = Field(default_factory=list, description="Danh sách các dị ứng thuốc/thức ăn")

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[List[str]] = None

class PatientOut(PatientBase):
    id: str = Field(..., description="MongoDB ObjectId dạng chuỗi")
    created_at: datetime

    class Config:
        populate_by_name = True
