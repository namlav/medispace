"""
Script sinh Dummy Data đạt định mức môn NoSQL:
- >= 100 Hồ sơ Bệnh nhân (Collection: patients)
- >= 100+ Lượt khám bệnh đa chuyên khoa (Collection: medical_records)
  Phân bổ đều vào 3 chuyên khoa: Tim Mạch, Da Liễu, Răng - Hàm - Mặt.
"""

import sys
import random
from pathlib import Path
from datetime import datetime, timedelta

# Đảm bảo import được backend modules
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from backend.app.core.database import get_db, get_patients_collection, get_records_collection
from backend.app.core.config import settings

# Danh sách họ, tên đệm, tên để tạo họ tên người Việt Nam tự nhiên
HO_LIST = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương"]
DEM_NAM = ["Văn", "Đức", "Hữu", "Minh", "Quốc", "Gia", "Thành", "Công", "Trọng", "Bảo"]
DEM_NU = ["Thị", "Ngọc", "Thu", "Mai", "Phương", "Thanh", "Khánh", "Mỹ", "Ánh", "Hải"]
TEN_NAM = ["An", "Bình", "Cường", "Dũng", "Đạt", "Hải", "Hiếu", "Hùng", "Huy", "Khoa", "Long", "Nam", "Phong", "Phúc", "Quân", "Sơn", "Tâm", "Thắng", "Tùng", "Việt"]
TEN_NU = ["Anh", "Chi", "Dung", "Giang", "Hà", "Hằng", "Hoa", "Hương", "Lan", "Linh", "Mai", "Nga", "Ngọc", "Nhung", "Phương", "Quỳnh", "Thảo", "Trang", "Uyên", "Vân"]

CITIES = ["Hà Nội", "TP. Hồ Chí Minh", "Đà Nẵng", "Cần Thơ", "Hải Phòng", "Bình Dương", "Đồng Nai", "Nghệ An", "Huế", "Quảng Ninh"]
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
ALLERGIES_SAMPLE = [
    "Dị ứng Penicillin", "Dị ứng Aspirin", "Dị ứng hải sản", "Dị ứng phấn hoa", 
    "Dị ứng Paracetamol", "Dị ứng thuốc cản quang", "Dị ứng thời tiết", "Không có dị ứng"
]

DOCTORS = {
    "TIM_MACH": ["BS. CKII Nguyễn Văn Hùng", "ThS. BS Trần Minh Tâm", "BS. CKI Lê Quốc Bảo"],
    "DA_LIEU": ["BS. CKII Phạm Thu Hằng", "ThS. BS Đỗ Mỹ Linh", "BS. CKI Vũ Phương Thảo"],
    "RANG_HAM_MAT": ["BS. CKII Hoàng Gia Huy", "ThS. BS Ngô Thành Đạt", "BS. CKI Bùi Thị Mai"]
}

def generate_random_patient(index: int) -> dict:
    gender = "Nam" if random.random() > 0.5 else "Nữ"
    if gender == "Nam":
        full_name = f"{random.choice(HO_LIST)} {random.choice(DEM_NAM)} {random.choice(TEN_NAM)}"
    else:
        full_name = f"{random.choice(HO_LIST)} {random.choice(DEM_NU)} {random.choice(TEN_NU)}"
        
    birth_year = random.randint(1950, 2020)
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)
    dob = f"{birth_year:04d}-{birth_month:02d}-{birth_day:02d}"
    
    phone = f"09{random.randint(10000000, 99999999)}"
    address = f"Số {random.randint(1, 250)}, Đường {random.choice(['Giải Phóng', 'Nguyễn Trãi', 'Cầu Giấy', 'Lê Lợi', 'Trần Hưng Đạo'])}, {random.choice(CITIES)}"
    
    allergies = []
    if random.random() < 0.35:
        allergies.append(random.choice(ALLERGIES_SAMPLE[:-1]))
    else:
        allergies.append("Không có dị ứng")

    return {
        "patient_code": f"BN-{index:04d}",
        "full_name": full_name,
        "dob": dob,
        "gender": gender,
        "phone": phone,
        "address": address,
        "blood_group": random.choice(BLOOD_GROUPS),
        "allergies": allergies,
        "created_at": datetime.utcnow() - timedelta(days=random.randint(30, 365))
    }

def generate_specialty_data(dept: str) -> tuple:
    """Trả về (symptoms, diagnosis, specialty_data, prescriptions) theo đặc thù từng khoa"""
    if dept == "TIM_MACH":
        symptoms = random.choice([
            "Hồi hộp, đánh trống ngực, khó thở khi leo cầu thang",
            "Đau thắt ngực lan ra vai trái, mệt mỏi kéo dài",
            "Chóng mặt, huyết áp đo tại nhà dao động 150-160 mmHg",
            "Khám định kỳ bệnh lý cao huyết áp và rối loạn mỡ máu"
        ])
        diagnosis = random.choice([
            "Tăng huyết áp vô căn độ 2",
            "Thiếu máu cơ tim cục bộ mạn tính",
            "Rối loạn nhịp xoang, ngoại tâm thu thất",
            "Xơ vữa động mạch cảnh, rối loạn lipid máu"
        ])
        specialty_data = {
            "blood_pressure": {
                "systolic": random.randint(120, 180),
                "diastolic": random.randint(75, 110)
            },
            "heart_rate_bpm": random.randint(60, 115),
            "ecg_result": random.choice([
                "Nhịp xoang đều, tần số 75ck/phút",
                "ST chênh xuống 1mm ở V4-V6",
                "Phì đại thất trái do tăng gánh áp lực",
                "Nhịp xoang nhanh 105 lần/phút"
            ]),
            "ejection_fraction_ef": random.randint(45, 68),
            "cardiovascular_risk": random.choice(["Thấp", "Trung bình", "Cao", "Rất cao"])
        }
        prescriptions = [
            {"medicine_name": "Amlodipine", "dosage": "5mg", "quantity": 30, "usage": "Uống 1 viên vào 8h sáng"},
            {"medicine_name": "Atorvastatin", "dosage": "20mg", "quantity": 30, "usage": "Uống 1 viên vào 20h tối"},
            {"medicine_name": "Aspirin pH8", "dosage": "81mg", "quantity": 30, "usage": "Uống 1 viên sau ăn no"}
        ]
    elif dept == "DA_LIEU":
        symptoms = random.choice([
            "Ngứa dữ dội về đêm, nổi nhiều mảng đỏ ở cẳng tay",
            "Da mặt nổi nhiều mụn viêm, sưng đau kèm bã nhờn",
            "Xuất hiện các đốm vảy trắng bong tróc ở da đầu và khuỷu tay",
            "Dị ứng nổi mề đay sau khi ăn đồ biển"
        ])
        diagnosis = random.choice([
            "Viêm da tiếp xúc dị ứng cấp tính",
            "Trứng cá bọc mức độ trung bình",
            "Vảy nến thể mảng thông thường",
            "Viêm da tiết bã vùng mặt và da đầu"
        ])
        specialty_data = {
            "lesion_locations": random.sample(["Khuôn mặt", "Cẳng tay", "Lưng", "Vùng ngực", "Da đầu", "Cẳng chân"], k=random.randint(1, 3)),
            "lesion_type": random.choice(["Mảng hồng ban giới hạn rõ", "Sẩn viêm mủ hoại tử", "Mụn nước mọc thành chùm", "Vảy tiết dày màu bạc"]),
            "pruritus_level": random.choice(["Nhẹ (2/10)", "Trung bình (5/10)", "Nặng (8/10)", "Rất dữ dội (10/10)"]),
            "patch_test": random.choice(["Chưa thực hiện", "Âm tính", "Dương tính (++) với hóa mỹ phẩm", "Nghi ngờ dị ứng kẽm"]),
            "is_contagious": random.choice([True, False])
        }
        prescriptions = [
            {"medicine_name": "Fucicort Cream", "dosage": "Tuýp 15g", "quantity": 1, "usage": "Thoa mỏng ngày 2 lần vào vùng tổn thương"},
            {"medicine_name": "Fexofenadine", "dosage": "180mg", "quantity": 14, "usage": "Uống 1 viên buổi sáng"}
        ]
    else: # RANG_HAM_MAT
        symptoms = random.choice([
            "Đau nhức răng hàm dưới buốt lên thái dương khi uống nước lạnh",
            "Chảy máu chân răng khi đánh răng, hôi miệng",
            "Răng khôn mọc lệch gây sưng nề góc hàm",
            "Kiểm tra răng định kỳ và lấy vôi răng"
        ])
        diagnosis = random.choice([
            "Sâu ngà sâu R36, R37",
            "Viêm quanh cuống răng mạn tính",
            "Viêm nướu tiến triển do vôi răng độ 3",
            "Lợi trùm răng khôn hàm dưới R48"
        ])
        teeth = [11, 21, 26, 36, 37, 38, 46, 47, 48]
        sample_teeth = random.sample(teeth, k=random.randint(1, 3))
        specialty_data = {
            "dental_chart": [
                {
                    "tooth_number": t,
                    "condition": random.choice(["Sâu men", "Sâu ngà buốt tủy", "Vỡ mẻ thân răng", "Mọc lệch đâm R kế cận"]),
                    "treatment": random.choice(["Hàn trám composite", "Điều trị tủy phục hồi", "Chỉ định nhổ bỏ", "Cắt lợi trùm"])
                }
                for t in sample_teeth
            ],
            "tartar_grade": random.randint(1, 3),
            "gingivitis": random.choice([True, False]),
            "oral_hygiene_score": random.choice(["Kém", "Trung bình", "Khá tốt"])
        }
        prescriptions = [
            {"medicine_name": "Rodogyl", "dosage": "Hộp 20 viên", "quantity": 1, "usage": "Uống 2 viên/ngày chia 2 lần sau ăn"},
            {"medicine_name": "Nước súc miệng Chlorohexidine 0.12%", "dosage": "Chai 250ml", "quantity": 1, "usage": "Súc miệng 15ml ngày 3 lần"}
        ]
        
    return symptoms, diagnosis, specialty_data, prescriptions

def seed_database(num_patients: int = 120, min_records: int = 150):
    print(f"[*] Bắt đầu kết nối MongoDB...")
    db = get_db()
    patients_col = get_patients_collection()
    records_col = get_records_collection()
    
    # Dọn dẹp dữ liệu cũ (reset collection)
    print("[-] Xóa dữ liệu cũ trong collection 'patients' và 'medical_records'...")
    patients_col.delete_many({})
    records_col.delete_many({})
    
    print(f"[+] Đang tạo {num_patients} hồ sơ bệnh nhân mẫu...")
    patient_docs = [generate_random_patient(i + 1) for i in range(num_patients)]
    insert_res = patients_col.insert_many(patient_docs)
    patient_ids = [str(pid) for pid in insert_res.inserted_ids]
    print(f"[✓] Đã chèn thành công {len(patient_ids)} bệnh nhân.")
    
    print(f"[+] Đang tạo {min_records} bệnh án đa chuyên khoa...")
    departments = ["TIM_MACH", "DA_LIEU", "RANG_HAM_MAT"]
    record_docs = []
    
    record_counter = 1
    # Đảm bảo mỗi bệnh nhân có ít nhất 1 lượt khám, một số bệnh nhân có nhiều lượt khám để test tỷ lệ tái khám
    for pid in patient_ids:
        # 60% bệnh nhân khám 1 lần, 25% khám 2 lần, 15% khám 3-4 lần
        r = random.random()
        if r < 0.60:
            num_visits = 1
        elif r < 0.85:
            num_visits = 2
        else:
            num_visits = random.randint(3, 4)
            
        base_date = datetime.utcnow() - timedelta(days=random.randint(60, 300))
        for v in range(num_visits):
            dept = random.choice(departments)
            doctor = random.choice(DOCTORS[dept])
            symptoms, diagnosis, specialty_data, prescriptions = generate_specialty_data(dept)
            
            visit_date = base_date + timedelta(days=v * random.randint(14, 45))
            follow_up = random.choice([True, False])
            follow_up_date = visit_date + timedelta(days=30) if follow_up else None
            
            rec = {
                "patient_id": pid,
                "record_code": f"BA-2026-{record_counter:04d}",
                "department": dept,
                "doctor_name": doctor,
                "visit_date": visit_date,
                "symptoms": symptoms,
                "diagnosis": diagnosis,
                "specialty_data": specialty_data,
                "prescriptions": prescriptions,
                "follow_up_required": follow_up,
                "follow_up_date": follow_up_date,
                "created_at": visit_date
            }
            record_docs.append(rec)
            record_counter += 1
            
    records_col.insert_many(record_docs)
    print(f"[✓] Đã chèn thành công {len(record_docs)} hồ sơ bệnh án đa chuyên khoa.")
    
    # Thống kê nhanh kết quả
    print("\n================== TỔNG KẾT BỘ DỮ LIỆU MẪU ==================")
    print(f"Tổng số bệnh nhân (patients): {patients_col.count_documents({})}")
    print(f"Tổng số bệnh án (medical_records): {records_col.count_documents({})}")
    for d in departments:
        cnt = records_col.count_documents({"department": d})
        print(f" - Chuyên khoa {d:15s}: {cnt} ca bệnh")
    print("============================================================\n")

if __name__ == "__main__":
    seed_database()
