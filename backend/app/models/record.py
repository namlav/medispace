from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class DepartmentEnum(str, Enum):
    TIM_MACH = "TIM_MACH"
    DA_LIEU = "DA_LIEU"
    RANG_HAM_MAT = "RANG_HAM_MAT"

class PrescriptionItem(BaseModel):
    medicine_name: str = Field(..., description="Tên thuốc")
    dosage: str = Field(..., description="Hàm lượng / Quy cách (ví dụ: 500mg, Chai 100ml)")
    quantity: int = Field(..., gt=0, description="Số lượng cấp phát")
    usage: str = Field(..., description="Hướng dẫn sử dụng (ví dụ: Uống sau ăn 1 viên x 2 lần/ngày)")

class MedicalRecordBase(BaseModel):
    patient_id: str = Field(..., description="ID của bệnh nhân (tham chiếu đến patients)")
    record_code: str = Field(..., description="Mã bệnh án duy nhất (ví dụ: BA-2026-001)")
    department: DepartmentEnum = Field(..., description="Chuyên khoa khám bệnh")
    doctor_name: str = Field(..., description="Bác sĩ phụ trách khám")
    visit_date: datetime = Field(default_factory=datetime.utcnow, description="Thời gian khám")
    symptoms: str = Field(..., description="Triệu chứng / Lý do đến khám")
    diagnosis: str = Field(..., description="Chẩn đoán của bác sĩ")
    
    # Trường Schema-less lưu trữ linh hoạt theo chuyên khoa
    specialty_data: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Dữ liệu đặc thù theo chuyên khoa (Tim Mạch, Da Liễu, Răng Hàm Mặt)"
    )
    
    # Đơn thuốc nhúng (Embedded Document Array)
    prescriptions: List[PrescriptionItem] = Field(
        default_factory=list, 
        description="Danh sách các loại thuốc được kê trong đợt khám"
    )
    
    follow_up_required: bool = Field(default=False, description="Có chỉ định tái khám hay không")
    follow_up_date: Optional[datetime] = Field(None, description="Thời gian hẹn tái khám")

class MedicalRecordCreate(MedicalRecordBase):
    pass

class MedicalRecordUpdate(BaseModel):
    doctor_name: Optional[str] = None
    symptoms: Optional[str] = None
    diagnosis: Optional[str] = None
    specialty_data: Optional[Dict[str, Any]] = None
    prescriptions: Optional[List[PrescriptionItem]] = None
    follow_up_required: Optional[bool] = None
    follow_up_date: Optional[datetime] = None

class MedicalRecordOut(MedicalRecordBase):
    id: str = Field(..., description="MongoDB ObjectId dạng chuỗi")
    created_at: datetime

    class Config:
        populate_by_name = True
