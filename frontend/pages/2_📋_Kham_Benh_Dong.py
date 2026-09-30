import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

from backend.app.services.patient_service import PatientService
from backend.app.services.record_service import RecordService
from backend.app.models.record import MedicalRecordCreate, PrescriptionItem, DepartmentEnum

st.set_page_config(page_title="Lập Bệnh Án Động | MediSpace", page_icon="📋", layout="wide")

st.title("📋 Khám Bệnh & Lập Hồ Sơ Bệnh Án Động (Schema-less)")
st.info("💡 **Tính năng nổi bật:** Khi chọn Chuyên khoa khác nhau, Form nhập liệu sẽ tự động thay đổi các trường dữ liệu lâm sàng đặc thù. Tất cả được lưu trong cùng collection `medical_records` mà không cần định nghĩa cứng bảng như SQL.")

# 1. Chọn Bệnh Nhân
patients, total = PatientService.list_patients(skip=0, limit=200)
if not patients:
    st.warning("Chưa có bệnh nhân nào trong hệ thống! Vui lòng tạo bệnh nhân hoặc chạy `scripts/seed_data.py` trước.")
    st.stop()

patient_options = {f"{p.get('patient_code')} - {p.get('full_name')} ({p.get('gender')}, {p.get('dob')})": p.get('id') for p in patients}
selected_patient_label = st.selectbox("1. Chọn Bệnh Nhân Thăm Khám:", list(patient_options.keys()))
selected_patient_id = patient_options[selected_patient_label]

col_main1, col_main2 = st.columns(2)
with col_main1:
    selected_dept = st.selectbox(
        "2. Chọn Chuyên Khoa Khám:",
        options=[DepartmentEnum.TIM_MACH.value, DepartmentEnum.DA_LIEU.value, DepartmentEnum.RANG_HAM_MAT.value],
        format_func=lambda x: {
            "TIM_MACH": "❤️ Khoa Tim Mạch",
            "DA_LIEU": "🔬 Khoa Da Liễu",
            "RANG_HAM_MAT": "🦷 Khoa Răng - Hàm - Mặt"
        }.get(x, x)
    )
    doctor_name = st.text_input("Bác sĩ phụ trách:", value="BS. CKII Nguyễn Văn Hùng" if selected_dept == "TIM_MACH" else ("BS. CKI Trần Thị B" if selected_dept == "DA_LIEU" else "BS. CKI Lê Hoàng C"))

with col_main2:
    record_code = st.text_input("Mã phiếu khám:", value=f"BA-{datetime.utcnow().strftime('%Y%m%d')}-{datetime.utcnow().strftime('%H%M%S')}")
    symptoms = st.text_input("Lý do khám / Triệu chứng lâm sàng:", placeholder="Ví dụ: Đau tức ngực, hồi hộp...")
    diagnosis = st.text_input("Chẩn đoán bệnh:", placeholder="Ví dụ: Tăng huyết áp độ 2...")

st.markdown("---")
st.subheader(f"🩺 Dữ Liệu Đặc Thù Của {selected_dept} (Dynamic Schema)")

specialty_data = {}

# Dynamic Form tùy theo chuyên khoa
if selected_dept == DepartmentEnum.TIM_MACH.value:
    c1, c2, c3 = st.columns(3)
    with c1:
        systolic = st.number_input("Huyết áp tâm thu (mmHg):", min_value=60, max_value=250, value=140)
        diastolic = st.number_input("Huyết áp tâm trương (mmHg):", min_value=40, max_value=150, value=90)
    with c2:
        heart_rate = st.number_input("Nhịp tim (lần/phút):", min_value=40, max_value=200, value=82)
        ef = st.number_input("Chỉ số phân suất tống máu EF (%):", min_value=20, max_value=85, value=58)
    with c3:
        ecg = st.selectbox("Kết quả Điện tâm đồ (ECG):", [
            "Nhịp xoang bình thường",
            "Nhịp xoang nhanh, ST chênh xuống nhẹ",
            "Ngoại tâm thu thất rải rác",
            "Phì đại thất trái"
        ])
        risk = st.selectbox("Phân tầng nguy cơ tim mạch:", ["Thấp", "Trung bình", "Cao", "Rất cao"])
        
    specialty_data = {
        "blood_pressure": {"systolic": systolic, "diastolic": diastolic},
        "heart_rate_bpm": heart_rate,
        "ejection_fraction_ef": ef,
        "ecg_result": ecg,
        "cardiovascular_risk": risk
    }

elif selected_dept == DepartmentEnum.DA_LIEU.value:
    c1, c2 = st.columns(2)
    with c1:
        locations = st.multiselect("Vị trí tổn thương da:", ["Khuôn mặt", "Cẳng tay", "Bàn tay", "Lưng", "Vùng ngực", "Da đầu", "Cẳng chân"], default=["Cẳng tay"])
        lesion_type = st.selectbox("Loại thương tổn đặc trưng:", [
            "Mảng hồng ban giới hạn rõ",
            "Sẩn viêm, mụn mủ hoại tử",
            "Mụn nước mọc thành chùm rải rác",
            "Vảy nến bong tróc màu bạc",
            "Mảng thâm sạm tăng sắc tố"
        ])
    with c2:
        pruritus = st.select_slider("Mức độ ngứa:", options=["Không ngứa (0)", "Nhẹ (2/10)", "Trung bình (5/10)", "Nặng (8/10)", "Dữ dội (10/10)"], value="Trung bình (5/10)")
        patch_test = st.text_input("Kết quả xét nghiệm áp bì (Patch test):", value="Âm tính")
        is_contagious = st.checkbox("Có nguy cơ lây nhiễm sang người khác", value=False)
        
    specialty_data = {
        "lesion_locations": locations,
        "lesion_type": lesion_type,
        "pruritus_level": pruritus,
        "patch_test": patch_test,
        "is_contagious": is_contagious
    }

elif selected_dept == DepartmentEnum.RANG_HAM_MAT.value:
    c1, c2 = st.columns(2)
    with c1:
        tooth_input = st.text_input("Vị trí răng tổn thương (cách nhau dấu phẩy, VD: 36, 46):", "36, 46")
        tooth_cond = st.selectbox("Tình trạng tổn thương răng:", ["Sâu ngà buốt tủy", "Sâu men răng nhẹ", "Vỡ mẻ thân răng", "Răng khôn mọc lệch đâm R lân cận"])
        tooth_treatment = st.selectbox("Hướng điều trị:", ["Hàn trám composite", "Điều trị tủy phục hồi", "Chỉ định nhổ bỏ", "Cắt lợi trùm"])
    with c2:
        tartar = st.slider("Mức độ cao răng (Tartar Grade 0-3):", min_value=0, max_value=3, value=2)
        gingivitis = st.checkbox("Có viêm nướu / Chảy máu chân răng", value=True)
        hygiene = st.selectbox("Đánh giá vệ sinh răng miệng:", ["Kém", "Trung bình", "Tốt"])
        
    teeth_list = [int(t.strip()) for t in tooth_input.split(",") if t.strip().isdigit()]
    specialty_data = {
        "dental_chart": [{"tooth_number": t, "condition": tooth_cond, "treatment": tooth_treatment} for t in teeth_list],
        "tartar_grade": tartar,
        "gingivitis": gingivitis,
        "oral_hygiene_score": hygiene
    }

st.markdown("---")
# 3. Kê đơn thuốc lồng (Embedded Prescriptions)
st.subheader("💊 Kê Đơn Thuốc (Embedded Document Array)")
col_p1, col_p2, col_p3, col_p4 = st.columns(4)
with col_p1:
    med_name = st.text_input("Tên thuốc:", "Amlodipine" if selected_dept == "TIM_MACH" else ("Fucicort Cream" if selected_dept == "DA_LIEU" else "Rodogyl"))
with col_p2:
    med_dose = st.text_input("Hàm lượng/Đơn vị:", "5mg" if selected_dept == "TIM_MACH" else ("Tuýp 15g" if selected_dept == "DA_LIEU" else "Viên nén"))
with col_p3:
    med_qty = st.number_input("Số lượng:", min_value=1, max_value=100, value=30 if selected_dept == "TIM_MACH" else 1)
with col_p4:
    med_usage = st.text_input("Hướng dẫn sử dụng:", "Uống 1 viên vào 8h sáng sau ăn")

col_follow1, col_follow2 = st.columns(2)
with col_follow1:
    follow_up = st.checkbox("Yêu cầu hẹn tái khám", value=True)
with col_follow2:
    follow_up_date = st.date_input("Ngày hẹn tái khám") if follow_up else None

if st.button("💾 Xác Nhận & Lưu Bệnh Án Vào MongoDB", type="primary", use_container_width=True):
    prescriptions = [
        PrescriptionItem(
            medicine_name=med_name,
            dosage=med_dose,
            quantity=med_qty,
            usage=med_usage
        )
    ]
    
    record_create = MedicalRecordCreate(
        patient_id=selected_patient_id,
        record_code=record_code,
        department=selected_dept,
        doctor_name=doctor_name,
        visit_date=datetime.utcnow(),
        symptoms=symptoms if symptoms else "Khám theo triệu chứng lâm sàng",
        diagnosis=diagnosis if diagnosis else "Theo dõi chẩn đoán chuyên khoa",
        specialty_data=specialty_data,
        prescriptions=prescriptions,
        follow_up_required=follow_up,
        follow_up_date=datetime.combine(follow_up_date, datetime.min.time()) if follow_up_date else None
    )
    
    try:
        saved_record = RecordService.create_record(record_create)
        st.success(f"🎉 Đã lưu thành công hồ sơ bệnh án mã `{saved_record.get('record_code')}` vào MongoDB!")
        st.caption("Document được lưu trực tiếp dạng BSON/JSON vào collection 'medical_records':")
        st.json(saved_record)
    except Exception as e:
        st.error(f"Lỗi khi lưu bệnh án: {e}")
