import re
import unicodedata
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

VOWELS_PATTERN = r"[aáàảãạăắằẳẵặâấầẩẫậeéèẻẽẹêếềểễệiíìỉĩịoóòỏõọôốồổỗộơớờởỡợuúùủũụưứừửữựyýỳỷỹỵ]"
SPAM_SEQUENCES = ["asdf", "sdfg", "dfgh", "ghjk", "hjkl", "qwerty", "zxcv", "qwer", "wert", "rtyu", "tyui", "yuio", "uiop"]

def validate_patient_name(name: str) -> tuple[bool, str]:
    """
    Kiểm tra tính hợp lệ của họ tên bệnh nhân:
    - Không để trống, độ dài từ 2 đến 50 ký tự.
    - Không chứa chữ số, không chứa ký tự đặc biệt.
    - Không chứa ký tự lặp liên tiếp (>= 3 ký tự, ví dụ: aaaaa, bbb).
    - Không chứa chuỗi phím cào (asdf, qwerty,...).
    - Mỗi âm tiết phải có ít nhất 1 nguyên âm, độ dài âm tiết <= 8 ký tự, không có cụm 4 phụ âm liên tiếp.
    """
    if not name or not isinstance(name, str):
        return False, "Họ và tên không được để trống."
    
    raw = unicodedata.normalize("NFC", name.strip())
    if len(raw) < 2:
        return False, "Họ và tên quá ngắn (ít nhất 2 ký tự)."
    if len(raw) > 50:
        return False, "Họ và tên quá dài (tối đa 50 ký tự)."
    
    # 1. Chữ số
    if any(ch.isdigit() for ch in raw):
        return False, "Họ và tên không được chứa chữ số."
    
    # 2. Ký tự đặc biệt
    name_regex = r"^[a-zA-ZàáảãạăắằẳẵặâấầẩẫậèéèẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵĐđ\s]+$"
    if not re.match(name_regex, raw):
        return False, "Họ và tên không được chứa ký tự đặc biệt."
    
    # 3. Ký tự lặp liên tiếp (>= 3 ký tự liên tiếp giống nhau, ví dụ: aaaaa, bbb)
    no_space = raw.replace(" ", "")
    if re.search(r"(.)\1{2,}", no_space, re.IGNORECASE):
        return False, "Họ và tên không hợp lệ (chứa chuỗi ký tự lặp liên tiếp)."
    
    # 4. Chuỗi phím cào (asdf, qwerty,...)
    lower_raw = raw.lower()
    for seq in SPAM_SEQUENCES:
        if seq in lower_raw:
            return False, f"Họ và tên có dấu hiệu spam bàn phím ('{seq}')."
            
    # 5. Kiểm tra từng từ (âm tiết)
    words = raw.split()
    if not words:
        return False, "Họ và tên không được để trống."
    
    for w in words:
        w_norm = unicodedata.normalize("NFC", w)
        # Mỗi từ phải có ít nhất 1 nguyên âm
        if not re.search(VOWELS_PATTERN, w_norm, re.IGNORECASE):
            return False, f"Từ '{w}' không hợp lệ (không chứa bất kỳ nguyên âm nào)."
        
        # Một âm tiết tên người hợp lệ không dài quá 8 ký tự
        if len(w_norm) > 8:
            return False, f"Từ '{w}' quá dài bất thường đối với tên người ({len(w_norm)} ký tự)."
        
        # Cụm phụ âm liên tiếp >= 4
        cons_clusters = re.split(VOWELS_PATTERN, w_norm, flags=re.IGNORECASE)
        for c in cons_clusters:
            if len(c) >= 4:
                return False, f"Cụm phụ âm '{c}' trong từ '{w}' không hợp lệ."
                
    return True, ""

class PatientBase(BaseModel):
    patient_code: str = Field(..., description="Mã bệnh nhân duy nhất (ví dụ: BN-1001)")
    full_name: str = Field(..., description="Họ và tên bệnh nhân")
    dob: str = Field(..., description="Ngày sinh (YYYY-MM-DD)")
    gender: str = Field(..., description="Giới tính: Nam, Nữ, Khác")
    phone: Optional[str] = Field(None, description="Số điện thoại liên hệ")
    address: Optional[str] = Field(None, description="Địa chỉ thường trú")
    blood_group: Optional[str] = Field(None, description="Nhóm máu: A, B, AB, O (+/-)")
    allergies: List[str] = Field(default_factory=list, description="Danh sách các dị ứng thuốc/thức ăn")

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        ok, msg = validate_patient_name(v)
        if not ok:
            raise ValueError(msg)
        return unicodedata.normalize("NFC", v.strip()).title()

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    patient_code: Optional[str] = None
    full_name: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[List[str]] = None

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            ok, msg = validate_patient_name(v)
            if not ok:
                raise ValueError(msg)
            return unicodedata.normalize("NFC", v.strip()).title()
        return v

class PatientOut(PatientBase):
    id: str = Field(..., description="MongoDB ObjectId dạng chuỗi")
    created_at: datetime

    class Config:
        populate_by_name = True
