import sys
from pathlib import Path
from datetime import datetime, timezone
from html import escape
import pandas as pd
import streamlit as st

# =====================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN & GIAO DIỆN HỆ THỐNG
# =====================================================================
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from frontend.api_client import (
    api_get_patients,
    api_get_records,
    api_create_record,
    api_update_record,
    api_delete_record,
    api_get_next_record_code,
)
from frontend.ui_utils import (
    load_css,
    format_number,
    get_icon,
    render_sidebar_branding,
    render_workstation_header,
    render_kpi_card,
    render_workstation_footer,
    render_pagination,
)

DEPARTMENTS = ["TIM_MACH", "DA_LIEU", "RANG_HAM_MAT"]
DEPT_LABELS = {
    "TIM_MACH": "Tim Mạch",
    "DA_LIEU": "Da Liễu",
    "RANG_HAM_MAT": "Răng - Hàm - Mặt",
}

st.set_page_config(
    page_title="MediSpace | Khám Bệnh Đa Chuyên Khoa",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Nạp hệ thống CSS Oceanic Workstation
load_css()

# Hiển thị nhận diện thương hiệu trên Sidebar
render_sidebar_branding()

# =====================================================================
# 2. TRUY VẤN DỮ LIỆU TỔNG QUAN
# =====================================================================
try:
    _, total_records = api_get_records(skip=0, limit=1)
except Exception:
    st.error("Không kết nối được FastAPI Backend. Vui lòng kiểm tra cổng 8000.", icon="⚠️")
    st.stop()

# =====================================================================
# 3. HEADER WORKSTATION (OCEANIC BLUE)
# =====================================================================
render_workstation_header(
    title="Bàn Khám Bệnh Động Đa Chuyên Khoa",
    subtitle="Mô hình bệnh án đa hình thức (Polymorphic Document) và kê đơn thuốc nhúng (Embedded Prescriptions)",
    badge_label=f"{format_number(total_records)} BỆNH ÁN ĐÃ LƯU",
    badge_status="live",
    icon_name="record",
)

# =====================================================================
# 4. CHỈ SỐ KPI LÂM SÀNG
# =====================================================================
c1, c2, c3 = st.columns(3)

with c1:
    render_kpi_card(
        label="Tổng Lượt Khám",
        value=format_number(total_records),
        foot="Collection medical_records",
        icon_name="record",
        accent_color="#0284C7",
    )

with c2:
    render_kpi_card(
        label="Chuyên Khoa Đa Hình",
        value="03 Khoa",
        foot="Tim Mạch · Da Liễu · Răng Hàm Mặt",
        icon_name="heart",
        accent_color="#0369A1",
    )

with c3:
    render_kpi_card(
        label="Đơn Thuốc Nhúng",
        value="Single Read",
        foot="Embedded Prescriptions Array",
        icon_name="pill",
        accent_color="#075985",
    )

st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

# Khởi tạo session state lưu đơn thuốc động trong form tạo mới
if "prescriptions_list" not in st.session_state:
    st.session_state.prescriptions_list = []

# =====================================================================
# 5. CÁC PHÂN VÙNG CHỨC NĂNG (TABS)
# =====================================================================
tab_create, tab_list, tab_edit, tab_delete = st.tabs(
    [
        "Lập Bệnh Án Mới",
        "Tra Cứu & Danh Sách Bệnh Án",
        "Chỉnh Sửa Bệnh Án",
        "Xóa Bệnh Án",
    ]
)

# ---------------------------------------------------------------------
# TAB 1: LẬP BỆNH ÁN MỚI (POLYMORPHIC CLINICAL FORM)
# ---------------------------------------------------------------------
with tab_create:
    st.subheader("Phiếu Khám Bệnh Đa Chuyên Khoa")

    # Bước 1: Chọn bệnh nhân tiếp nhận
    st.markdown("##### 1. Tiếp Nhận Bệnh Nhân")
    search_p = st.text_input(
        "Tìm bệnh nhân vào khám (Mã BN, Họ tên, SĐT)",
        placeholder="Nhập BN-XXXX, tên bệnh nhân...",
        key="search_p_exam",
    )

    patients_exam, _ = api_get_patients(
        skip=0, limit=50, search=search_p.strip() if search_p else None
    )

    if not patients_exam:
        st.warning("Không tìm thấy bệnh nhân. Vui lòng tạo hồ sơ bệnh nhân trước tại phân hệ Bệnh Nhân.", icon="⚠️")
        st.stop()

    patient_opts = {
        f"{p.get('patient_code')} - {p.get('full_name')} ({p.get('gender')}, NS: {p.get('dob')})": p
        for p in patients_exam
    }
    selected_p_label = st.selectbox("Chọn bệnh nhân khám:", options=list(patient_opts.keys()), key="select_p_exam")
    current_patient = patient_opts[selected_p_label]
    current_patient_id = str(current_patient.get("_id") or current_patient.get("id"))

<<<<<<< HEAD
    selected_patient_label = st.selectbox("1. Chọn Bệnh Nhân Thăm Khám:", list(patient_options.keys()), key="select_patient_create")
    selected_patient_id = patient_options[selected_patient_label]

    col_main1, col_main2 = st.columns(2)
    with col_main1:
        selected_dept = st.selectbox(
            "2. Chọn Chuyên Khoa Khám:",
            options=DEPARTMENTS,
            format_func=lambda x: {
                "TIM_MACH": "❤️ Khoa Tim Mạch",
                "DA_LIEU": "🔬 Khoa Da Liễu",
                "RANG_HAM_MAT": "🦷 Khoa Răng - Hàm - Mặt"
            }.get(x, x),
            key="select_dept_create"
        )
        doctor_name = st.text_input("Bác sĩ phụ trách:", value="BS. CKII Nguyễn Văn Hùng" if selected_dept == "TIM_MACH" else ("BS. CKI Trần Thị B" if selected_dept == "DA_LIEU" else "BS. CKI Lê Hoàng C"), key="doc_name_create")

    with col_main2:
        now_utc = datetime.now(timezone.utc)
        record_code = st.text_input("Mã phiếu khám:", value=f"BA-{now_utc.strftime('%Y%m%d')}-{now_utc.strftime('%H%M%S')}", key="rec_code_create")
        symptoms = st.text_input("Lý do khám / Triệu chứng lâm sàng:", placeholder="Ví dụ: Đau tức ngực, hồi hộp...", key="symp_create")
        diagnosis = st.text_input("Chẩn đoán bệnh:", placeholder="Ví dụ: Tăng huyết áp độ 2...", key="diag_create")

    st.markdown("---")
    st.subheader(f"🩺 Dữ Liệu Đặc Thù Của {selected_dept} (Dynamic Schema)")

    specialty_data = {}
    if selected_dept == "TIM_MACH":
        c1, c2, c3 = st.columns(3)
        with c1:
            systolic = st.number_input("Huyết áp tâm thu (mmHg):", min_value=60, max_value=250, value=140, key="c_sys")
            diastolic = st.number_input("Huyết áp tâm trương (mmHg):", min_value=40, max_value=150, value=90, key="c_dia")
        with c2:
            heart_rate = st.number_input("Nhịp tim (lần/phút):", min_value=40, max_value=200, value=82, key="c_hr")
            ef = st.number_input("Chỉ số phân suất tống máu EF (%):", min_value=20, max_value=85, value=58, key="c_ef")
        with c3:
            ecg = st.selectbox("Kết quả Điện tâm đồ (ECG):", [
                "Nhịp xoang bình thường",
                "Nhịp xoang nhanh, ST chênh xuống nhẹ",
                "Ngoại tâm thu thất rải rác",
                "Phì đại thất trái"
            ], key="c_ecg")
            risk = st.selectbox("Phân tầng nguy cơ tim mạch:", ["Thấp", "Trung bình", "Cao", "Rất cao"], key="c_risk")
            
        specialty_data = {
            "blood_pressure": {"systolic": systolic, "diastolic": diastolic},
            "heart_rate_bpm": heart_rate,
            "ejection_fraction_ef": ef,
            "ecg_result": ecg,
            "cardiovascular_risk": risk
        }
    elif selected_dept == "DA_LIEU":
        c1, c2 = st.columns(2)
        with c1:
            locations = st.multiselect("Vị trí tổn thương da:", ["Khuôn mặt", "Cẳng tay", "Bàn tay", "Lưng", "Vùng ngực", "Da đầu", "Cẳng chân"], default=["Cẳng tay"], key="d_loc")
            lesion_type = st.selectbox("Loại thương tổn đặc trưng:", [
                "Mảng hồng ban giới hạn rõ",
                "Sẩn viêm, mụn mủ hoại tử",
                "Mụn nước mọc thành chùm rải rác",
                "Vảy nến bong tróc màu bạc",
                "Mảng thâm sạm tăng sắc tố"
            ], key="d_type")
        with c2:
            pruritus = st.select_slider("Mức độ ngứa:", options=["Không ngứa (0)", "Nhẹ (2/10)", "Trung bình (5/10)", "Nặng (8/10)", "Dữ dội (10/10)"], value="Trung bình (5/10)", key="d_pru")
            patch_test = st.text_input("Kết quả xét nghiệm áp bì (Patch test):", value="Âm tính", key="d_patch")
            is_contagious = st.checkbox("Có nguy cơ lây nhiễm sang người khác", value=False, key="d_con")
            
        specialty_data = {
            "lesion_locations": locations,
            "lesion_type": lesion_type,
            "pruritus_level": pruritus,
            "patch_test": patch_test,
            "is_contagious": is_contagious
        }
    elif selected_dept == "RANG_HAM_MAT":
        c1, c2 = st.columns(2)
        with c1:
            tooth_input = st.text_input("Vị trí răng tổn thương (VD: 36, 46):", "36, 46", key="r_tooth")
            tooth_cond = st.selectbox("Tình trạng tổn thương răng:", ["Sâu ngà buốt tủy", "Sâu men răng nhẹ", "Vỡ mẻ thân răng", "Răng khôn mọc lệch đâm R lân cận"], key="r_cond")
            tooth_treatment = st.selectbox("Hướng điều trị:", ["Hàn trám composite", "Điều trị tủy phục hồi", "Chỉ định nhổ bỏ", "Cắt lợi trùm"], key="r_treat")
        with c2:
            tartar = st.slider("Mức độ cao răng (Tartar Grade 0-3):", min_value=0, max_value=3, value=2, key="r_tar")
            gingivitis = st.checkbox("Có viêm nướu / Chảy máu chân răng", value=True, key="r_ging")
            hygiene = st.selectbox("Đánh giá vệ sinh răng miệng:", ["Kém", "Trung bình", "Tốt"], key="r_hyg")
            
        teeth_list = [int(t.strip()) for t in tooth_input.split(",") if t.strip().isdigit()]
        specialty_data = {
            "dental_chart": [{"tooth_number": t, "condition": tooth_cond, "treatment": tooth_treatment} for t in teeth_list],
            "tartar_grade": tartar,
            "gingivitis": gingivitis,
            "oral_hygiene_score": hygiene
        }

    st.markdown("---")
    st.subheader("💊 Kê Đơn Thuốc (Embedded Document Array)")
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        med_name = st.text_input("Tên thuốc:", "Amlodipine" if selected_dept == "TIM_MACH" else ("Fucicort Cream" if selected_dept == "DA_LIEU" else "Rodogyl"), key="med_name_create")
    with col_p2:
        med_dose = st.text_input("Hàm lượng/Đơn vị:", "5mg" if selected_dept == "TIM_MACH" else ("Tuýp 15g" if selected_dept == "DA_LIEU" else "Viên nén"), key="med_dose_create")
    with col_p3:
        med_qty = st.number_input("Số lượng:", min_value=1, max_value=100, value=30 if selected_dept == "TIM_MACH" else 1, key="med_qty_create")
    with col_p4:
        med_usage = st.text_input("Hướng dẫn sử dụng:", "Uống 1 viên vào 8h sáng sau ăn", key="med_usage_create")

    col_follow1, col_follow2 = st.columns(2)
    with col_follow1:
        follow_up = st.checkbox("Yêu cầu hẹn tái khám", value=True, key="follow_up_chk")
    with col_follow2:
        follow_up_date = st.date_input("Ngày hẹn tái khám", key="follow_up_dt") if follow_up else None

    if st.button("💾 Xác Nhận & Lưu Bệnh Án Vào MongoDB (qua API)", type="primary", width="stretch", key="btn_save_record"):
        prescriptions = [
            {
                "medicine_name": med_name,
                "dosage": med_dose,
                "quantity": med_qty,
                "usage": med_usage
            }
        ]
        
        record_payload = {
            "patient_id": selected_patient_id,
            "record_code": record_code,
            "department": selected_dept,
            "doctor_name": doctor_name,
            "visit_date": datetime.now(timezone.utc).isoformat(),
            "symptoms": symptoms if symptoms else "Khám theo triệu chứng lâm sàng",
            "diagnosis": diagnosis if diagnosis else "Theo dõi chẩn đoán chuyên khoa",
            "specialty_data": specialty_data,
            "prescriptions": prescriptions,
            "follow_up_required": follow_up,
            "follow_up_date": datetime.combine(follow_up_date, datetime.min.time()).isoformat() if follow_up_date else None
        }
        
        try:
            res, status_code = api_create_record(record_payload)
            if status_code in [200, 201]:
                st.toast("🎉 Đã lưu thành công hồ sơ bệnh án mới!", icon="✅")
                st.success("🎉 Đã lưu thành công hồ sơ bệnh án qua API!")
                st.rerun()
            else:
                st.error(f"Lỗi từ API: {res}")
        except Exception as e:
            st.error(f"Lỗi khi lưu bệnh án: {e}")

# ==========================================
# TAB 2: TRA CỨU & TÌM KIẾM HỒ SƠ BỆNH ÁN
# ==========================================
with tab_search:
    st.subheader("🔍 Tìm Kiếm & Xem Chi Tiết Bệnh Án")
    
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        search_query = st.text_input(
            "Tìm kiếm theo Mã bệnh án, Mã BN, Tên bệnh nhân, Chẩn đoán !", 
            key="search_record_query", 
            placeholder="Nhập từ khóa..."
        )
    with col_s2:
        filter_dept = st.selectbox(
            "Lọc theo chuyên khoa:",
            options=["Tất cả"] + DEPARTMENTS,
            format_func=lambda x: {
                "Tất cả": "🌐 Tất cả khoa",
                "TIM_MACH": "❤️ Tim Mạch",
                "DA_LIEU": "🔬 Da Liễu",
                "RANG_HAM_MAT": "🦷 Răng - Hàm - Mặt"
            }.get(x, x),
            key="filter_dept_search"
        )

    # 1. Gọi API lấy danh sách bệnh án (sau khi đã có search_query và filter_dept)
    try:
        dept_param = None if filter_dept == "Tất cả" else filter_dept
        response_data = api_client.get_records(
            search=search_query if search_query else None, 
            department=dept_param
        )
        records = response_data.get("items", [])
        total_rec = response_data.get("total", 0)
    except Exception:
        records = []
        total_rec = 0

    # 2. Trích xuất tên bác sĩ từ dữ liệu để kiểm tra
    doctor_names = set()
    for rec in records:
        doc_name = rec.get("doctor_name")
        if doc_name:
            doctor_names.add(doc_name.strip().lower())

    # 3. Kiểm tra nếu từ khóa nhập vào khớp với tên bác sĩ
    is_searching_doctor = False
    if search_query:
        query_clean = search_query.strip().lower()
        for doc_name in doctor_names:
            if query_clean in doc_name or doc_name in query_clean:
                is_searching_doctor = True
                break
    
    # 4. Hiển thị thông báo chặn nếu tìm theo tên bác sĩ
    if is_searching_doctor:
        st.error("🚫 Thông tin bác sĩ không được sử dụng trong tìm kiếm! Vui lòng chỉ tìm theo thông tin bệnh nhân.")
        records = []  # Xóa kết quả hiển thị

    try:
        dept_arg = None if filter_dept == "Tất cả" else filter_dept
        records, total_rec = api_get_records(
            skip=0,
            limit=200,
            department=dept_arg,
            search=search_query.strip() or None
        )

        st.write(f"Tìm thấy **{len(records)}** / **{total_rec}** hồ sơ bệnh án:")
        
        if records:
            for rec in records:
                rec_code_disp = rec.get("record_code", "N/A")
                dept_disp = rec.get("department", "N/A")
                doc_disp = rec.get("doctor_name", "N/A")
                diag_disp = rec.get("diagnosis", "Chưa có chẩn đoán")
                visit_dt = rec.get("visit_date", "N/A")
                
                p_id = str(rec.get("patient_id"))
                patient_info = patient_map.get(p_id, {})
                patient_code_disp = patient_info.get("patient_code", "Không rõ mã")
                patient_name_disp = patient_info.get("full_name", "Khách vãng lai")
                
                expander_label = f"📌 **[{rec_code_disp}]** | 🆔 **Mã BN:** `{patient_code_disp}` - **{patient_name_disp}** | Khoa: {dept_disp} | Chẩn đoán: {diag_disp}"
                
                with st.expander(expander_label):
                    c_info1, c_info2 = st.columns(2)
                    with c_info1:
                        st.markdown(f"**Mã phiếu khám:** `{rec_code_disp}`")
                        st.markdown(f"**Mã bệnh nhân:** `{patient_code_disp}`")
                        st.markdown(f"**Họ tên bệnh nhân:** **{patient_name_disp}**")
                        st.markdown(f"**Chuyên khoa:** {dept_disp}")
                    with c_info2:
                        st.markdown(f"**Bác sĩ phụ trách:** {doc_disp}")
                        st.markdown(f"**Ngày khám:** {visit_dt}")
                        st.markdown(f"**Triệu chứng:** {rec.get('symptoms', 'Không có')}")
                        st.markdown(f"**Chẩn đoán:** {diag_disp}")
                        st.markdown(f"**Hẹn tái khám:** {'Có' if rec.get('follow_up_required') else 'Không'}")
                    
                    st.markdown("---")
                    st.markdown("🩺 **Dữ Liệu Lâm Sàng Đặc Thù (Dynamic Specialty Data):**")
                    st.json(rec.get("specialty_data", {}))
                    
                    pres_list = rec.get("prescriptions", [])
                    if pres_list:
                        st.markdown("💊 **Đơn Thuốc Đã Kê:**")
                        st.dataframe(pres_list, width="stretch")
        else:
            st.warning("Không tìm thấy hồ sơ bệnh án nào phù hợp với điều kiện tìm kiếm.")
            
    except Exception as e:
        st.error(f"Lỗi khi tra cứu bệnh án: {e}")

# ==========================================
# TAB 3: CHỈNH SỬA HỒ SƠ BỆNH ÁN
# ==========================================
with tab_edit:
    st.subheader("✏️ Chỉnh Sửa Thông Tin Bệnh Án & Dữ Liệu Đặc Thù")
    search_edit = st.text_input("🔍 Tìm bệnh án cần chỉnh sửa (Mã BA, Mã BN, Tên BN):", key="search_edit_rec_tab")
    all_recs, _ = api_get_records(
        skip=0,
        limit=1000,
        search=search_edit.strip() or None
=======
    # Patient Sticky Banner
    allergies_display = (
        ", ".join(current_patient.get("allergies", []))
        if current_patient.get("allergies")
        else "Không ghi nhận"
    )
    st.markdown(
        f"""
        <div class="ms-patient-banner">
            <div class="ms-patient-info">
                <div>
                    <div style="font-size: 0.8rem; color: var(--ms-text-muted); text-transform: uppercase; font-weight: 700;">Bệnh nhân đang khám</div>
                    <div class="ms-patient-name">{escape(str(current_patient.get("full_name")))}</div>
                </div>
                <span class="ms-code-badge">{escape(str(current_patient.get("patient_code")))}</span>
            </div>
            <div class="ms-patient-vitals">
                <span class="ms-vital-tag">Ngày sinh: <strong>{current_patient.get("dob")}</strong></span>
                <span class="ms-vital-tag">Giới tính: <strong>{current_patient.get("gender")}</strong></span>
                <span class="ms-vital-tag">Nhóm máu: <strong>{current_patient.get("blood_group") or "Chưa rõ"}</strong></span>
                <span class="ms-vital-tag" style="background: var(--ms-triage-amber-bg); border-color: var(--ms-triage-amber-border); color: var(--ms-triage-amber);">Tiền sử dị ứng: <strong>{escape(allergies_display)}</strong></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
>>>>>>> 62656e23a6eacf371d3fc21696292e6f1fbaa3d3
    )

    # Bước 2: Chọn chuyên khoa khám bệnh
    st.markdown("##### 2. Chọn Chuyên Khoa Khám")
    selected_dept = st.radio(
        "Chuyên khoa tiếp nhận:",
        options=DEPARTMENTS,
        format_func=lambda d: f"{DEPT_LABELS[d]} ({d})",
        horizontal=True,
        key="radio_dept_exam",
    )

    # Form nhập bệnh án
    with st.form("form_create_medical_record"):
        st.markdown(f"##### 3. Thông Tin Lâm Sàng & Đặc Thù Chuyên Khoa: **{DEPT_LABELS[selected_dept]}**")

        f1, f2 = st.columns(2)
        with f1:
            auto_rec_code = api_get_next_record_code() or (
                f"BA-2026-{total_records + 1:04d}" if total_records < 9999 else f"BA-2026-{total_records + 1:05d}"
            )
            record_code_val = st.text_input(
                "Mã bệnh án (Tự động cấp tăng dần) *",
                value=auto_rec_code,
                disabled=True,
                help="Mã bệnh án được hệ thống tự động cấp theo hồ sơ cuối cùng + 1.",
            )
            doctor_name_val = st.text_input("Bác sĩ phụ trách khám *", value="BS.CKI Nguyễn Văn Y")
        with f2:
            symptoms_val = st.text_input("Triệu chứng / Lý do vào khám *", placeholder="Ví dụ: Đau ngực trái, khó thở khi gắng sức...")
            diagnosis_val = st.text_input("Chẩn đoán xác định *", placeholder="Ví dụ: Tăng huyết áp độ II, Bệnh tim thiếu máu cục bộ...")

        # Dữ liệu đặc thù theo chuyên khoa (Polymorphic schema)
        st.markdown(f"**Thông số lâm sàng chuyên khoa {DEPT_LABELS[selected_dept]}:**")
        specialty_data = {}

        if selected_dept == "TIM_MACH":
            tm_c1, tm_c2, tm_c3 = st.columns(3)
            with tm_c1:
                systolic = st.number_input("Huyết áp tâm thu (mmHg):", min_value=60, max_value=260, value=130)
                diastolic = st.number_input("Huyết áp tâm trương (mmHg):", min_value=40, max_value=160, value=85)
            with tm_c2:
                heart_rate = st.number_input("Nhịp tim (bpm):", min_value=30, max_value=220, value=78)
                ef = st.number_input("Phân suất tống máu EF (%):", min_value=10, max_value=90, value=60)
            with tm_c3:
                ecg = st.selectbox(
                    "Kết quả điện tâm đồ (ECG):",
                    ["Nhịp xoang bình thường", "Rung nhĩ", "Thiếu máu cơ tim", "Block nhánh trái", "Ngoại tâm thu thất"],
                )
                risk = st.selectbox("Phân tầng nguy cơ tim mạch:", ["Thấp", "Trung bình", "Cao", "Rất cao"], index=1)

            specialty_data = {
                "blood_pressure": {"systolic": systolic, "diastolic": diastolic},
                "heart_rate_bpm": heart_rate,
                "ejection_fraction_ef": ef,
                "ecg_result": ecg,
                "cardiovascular_risk": risk,
            }

        elif selected_dept == "DA_LIEU":
            dl_c1, dl_c2 = st.columns(2)
            with dl_c1:
                locations = st.multiselect(
                    "Vị trí thương tổn:",
                    ["Mặt", "Cổ", "Tay", "Chân", "Lưng", "Ngực", "Bụng", "Toàn thân"],
                    default=["Mặt", "Cổ"],
                )
                lesion_type = st.selectbox(
                    "Hình thái học thương tổn:",
                    ["Dát đỏ", "Sẩn ngứa", "Mụn nước", "Mảng vảy nến", "Mụn mủ", "Loét da", "Mề đay"],
                )
            with dl_c2:
                pruritus = st.slider("Thang điểm ngứa VAS (1-10):", min_value=1, max_value=10, value=4)
                patch_test = st.selectbox("Kết quả xét nghiệm dị nguyên (Patch test):", ["Âm tính", "Dương tính (+)", "Dương tính (++)", "Chưa thực hiện"])
                is_contagious = st.checkbox("Có nguy cơ lây nhiễm sinh học", value=False)

            specialty_data = {
                "lesion_locations": locations,
                "lesion_type": lesion_type,
                "pruritus_level": pruritus,
                "patch_test": patch_test,
                "is_contagious": is_contagious,
            }

        elif selected_dept == "RANG_HAM_MAT":
            rhm_c1, rhm_c2 = st.columns(2)
            with rhm_c1:
                tooth_input = st.text_input("Vị trí răng tổn thương (cách nhau bởi dấu phẩy):", value="16, 26, 37")
                tooth_cond = st.selectbox("Tình trạng răng:", ["Sâu ngà nông", "Sâu ngà sâu", "Viêm tủy cấp", "Mất răng", "Tụt lợi viêm nha chu"])
            with rhm_c2:
                tooth_treatment = st.selectbox("Kế hoạch điều trị:", ["Trám răng Composite", "Điều trị tủy nội nha", "Nhổ răng", "Cạo vôi & Đánh bóng"])
                panorex = st.selectbox("Phim X-quang toàn cảnh (Panorex):", ["Bình thường", "Tiêu xương ổ răng", "U nang chân răng", "Răng ngầm 38/48"])

            teeth_list = [int(t.strip()) for t in tooth_input.split(",") if t.strip().isdigit()]
            specialty_data = {
                "dental_chart": [
                    {"tooth_number": t, "condition": tooth_cond, "treatment": tooth_treatment}
                    for t in teeth_list
                ],
                "panorex_result": panorex,
            }

        # Kế hoạch tái khám
        st.markdown("##### 4. Kế Hoạch Tái Khám")
        rc1, rc2 = st.columns(2)
        with rc1:
            follow_up = st.checkbox("Chỉ định tái khám", value=True)
        with rc2:
            follow_up_date = st.date_input("Ngày hẹn tái khám") if follow_up else None

        st.divider()
        submitted_record = st.form_submit_button("Lưu Hồ Sơ Bệnh Án", type="primary", use_container_width=True)

        if submitted_record:
            if not record_code_val or not symptoms_val or not diagnosis_val:
                st.error("Vui lòng nhập đầy đủ Mã bệnh án, Triệu chứng và Chẩn đoán xác định.")
            else:
                record_payload = {
                    "patient_id": current_patient_id,
                    "record_code": record_code_val.strip(),
                    "department": selected_dept,
                    "doctor_name": doctor_name_val.strip(),
                    "visit_date": datetime.now(timezone.utc).isoformat(),
                    "symptoms": symptoms_val.strip(),
                    "diagnosis": diagnosis_val.strip(),
                    "specialty_data": specialty_data,
                    "prescriptions": st.session_state.prescriptions_list,
                    "follow_up_required": follow_up,
                    "follow_up_date": (
                        datetime.combine(follow_up_date, datetime.min.time()).isoformat()
                        if follow_up and follow_up_date
                        else None
                    ),
                }

                try:
                    res, status_code = api_create_record(record_payload)
                    if status_code in [200, 201]:
                        st.success(f"Lưu bệnh án thành công! Mã: {record_code_val} · Chuyên khoa: {DEPT_LABELS[selected_dept]}", icon="✅")
                        st.session_state.prescriptions_list = []
                        st.rerun()
                    else:
                        st.error(f"Lỗi phản hồi API Backend: {res}")
                except Exception as ex:
                    st.error(f"Lỗi khi lưu bệnh án: {ex}")

    # Bảng kê đơn thuốc nhúng
    st.markdown("##### 5. Đơn Thuốc Nhúng (Embedded Prescriptions)")
    with st.expander("Thêm thuốc vào đơn thuốc", expanded=True):
        m_col1, m_col2, m_col3, m_col4 = st.columns([3, 2, 1, 3])
        with m_col1:
            med_name = st.text_input("Tên biệt dược / hoạt chất", placeholder="Ví dụ: Amlodipine, Paracetamol...")
        with m_col2:
            med_dosage = st.text_input("Hàm lượng", placeholder="Ví dụ: 5mg, 500mg, Gói 2g")
        with m_col3:
            med_qty = st.number_input("Số lượng", min_value=1, max_value=300, value=30)
        with m_col4:
            med_usage = st.text_input("Hướng dẫn sử dụng", placeholder="Ví dụ: Uống 1 viên vào buổi sáng sau ăn")

        col_add_med, col_clear_med = st.columns([1, 4])
        with col_add_med:
            if st.button("Thêm vào đơn", type="secondary"):
                if med_name.strip():
                    st.session_state.prescriptions_list.append(
                        {
                            "medicine_name": med_name.strip(),
                            "dosage": med_dosage.strip(),
                            "quantity": int(med_qty),
                            "usage": med_usage.strip(),
                        }
                    )
                    st.toast(f"Đã thêm thuốc: {med_name}")
                    st.rerun()
                else:
                    st.warning("Vui lòng nhập tên thuốc.")
        with col_clear_med:
            if st.session_state.prescriptions_list and st.button("Xóa danh sách đơn thuốc"):
                st.session_state.prescriptions_list = []
                st.rerun()

    if st.session_state.prescriptions_list:
        st.markdown(f"**Danh mục thuốc đã kê ({len(st.session_state.prescriptions_list)} thuốc):**")
        df_curr_pres = pd.DataFrame(st.session_state.prescriptions_list)
        df_curr_pres.rename(
            columns={
                "medicine_name": "Tên thuốc",
                "dosage": "Hàm lượng",
                "quantity": "Số lượng",
                "usage": "Cách dùng",
            },
            inplace=True,
        )
        st.dataframe(df_curr_pres, use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có thuốc nào được kê cho bệnh án này.", icon="ℹ️")

# ---------------------------------------------------------------------
# TAB 2: TRA CỨU & DANH SÁCH BỆNH ÁN (PHÂN TRANG TỐI ĐA 50 HỒ SƠ/TRANG)
# ---------------------------------------------------------------------
with tab_list:
    st.subheader("Tra Cứu Danh Sách Bệnh Án Điện Tử")

    c_filt_dept, c_filt_search, c_filt_limit = st.columns([1, 2, 1])
    with c_filt_dept:
        dept_filter = st.selectbox(
            "Lọc theo chuyên khoa:",
            options=["TẤT CẢ"] + DEPARTMENTS,
            format_func=lambda d: "Tất cả các khoa" if d == "TẤT CẢ" else DEPT_LABELS[d],
            key="filter_dept_list",
        )
    with c_filt_search:
        search_rec = st.text_input(
            "Tìm kiếm theo mã BA, chẩn đoán hoặc triệu chứng:",
            placeholder="Ví dụ: BA-2026-0001, Tăng huyết áp...",
            key="filter_search_rec",
        )
    with c_filt_limit:
        rec_limit = st.selectbox(
            "Số lượng mỗi trang (tối đa 50):",
            options=[10, 20, 50],
            index=2,
            key="filter_limit_rec",
        )

    # Đặt lại về trang 1 khi thay đổi chuyên khoa, từ khóa hoặc cỡ trang
    curr_dept_val = dept_filter
    curr_rec_search = search_rec.strip() if search_rec else ""
    if (
        st.session_state.get("rec_last_dept") != curr_dept_val
        or st.session_state.get("rec_last_search") != curr_rec_search
        or st.session_state.get("rec_last_limit") != rec_limit
    ):
        st.session_state["rec_last_dept"] = curr_dept_val
        st.session_state["rec_last_search"] = curr_rec_search
        st.session_state["rec_last_limit"] = rec_limit
        st.session_state["record_page"] = 1
        st.session_state["record_page_jump_txt"] = "1"

    if "record_page" not in st.session_state:
        st.session_state["record_page"] = 1

    curr_rec_page = st.session_state["record_page"]
    skip_rec = (curr_rec_page - 1) * rec_limit

    records_matched, total_matched_recs = api_get_records(
        skip=skip_rec,
        limit=rec_limit,
        department=curr_dept_val if curr_dept_val != "TẤT CẢ" else None,
        search=curr_rec_search if curr_rec_search else None,
    )

    total_rec_pages = max(1, (total_matched_recs + rec_limit - 1) // rec_limit)
    if curr_rec_page > total_rec_pages:
        st.session_state["record_page"] = total_rec_pages
        curr_rec_page = total_rec_pages
        skip_rec = (curr_rec_page - 1) * rec_limit
        records_matched, total_matched_recs = api_get_records(
            skip=skip_rec,
            limit=rec_limit,
            department=curr_dept_val if curr_dept_val != "TẤT CẢ" else None,
            search=curr_rec_search if curr_rec_search else None,
        )

    start_rec_idx = skip_rec + 1 if total_matched_recs > 0 else 0
    end_rec_idx = min(skip_rec + len(records_matched), total_matched_recs)

    st.markdown(
        f"""
        <div style="font-size: 0.85rem; color: var(--ms-text-muted); margin-bottom: 0.75rem;">
            Tìm thấy <strong>{format_number(total_matched_recs)}</strong> bệnh án phù hợp · Hiển thị ca <strong>{start_rec_idx} - {end_rec_idx}</strong> (Trang <strong>{curr_rec_page}/{total_rec_pages}</strong>).
        </div>
        """,
        unsafe_allow_html=True,
    )

    if records_matched:
        for r in records_matched:
            r_dept = r.get("department", "CHUYÊN KHOA")
            r_date = r.get("visit_date", "")[:10]
            with st.expander(
                f"Mã: {r.get('record_code', '—')} · {DEPT_LABELS.get(r_dept, r_dept)} · Ngày: {r_date} · Chẩn đoán: {r.get('diagnosis', '—')}",
                expanded=False,
            ):
                rx1, rx2 = st.columns(2)
                with rx1:
                    st.markdown(f"**Bác sĩ phụ trách:** {r.get('doctor_name', '—')}")
                    st.markdown(f"**Triệu chứng:** {r.get('symptoms', '—')}")
                    st.markdown(f"**Chẩn đoán:** {r.get('diagnosis', '—')}")
                with rx2:
                    st.markdown(f"**Yêu cầu tái khám:** {'Có' if r.get('follow_up_required') else 'Không'}")
                    if r.get("follow_up_date"):
                        st.markdown(f"**Ngày hẹn tái khám:** {r.get('follow_up_date')[:10]}")

                s_data = r.get("specialty_data", {})
                if s_data:
                    st.markdown(f"**Dữ liệu lâm sàng đặc thù ({DEPT_LABELS.get(r_dept, r_dept)}):**")
                    st.json(s_data)

                pres = r.get("prescriptions", [])
                if pres:
                    st.markdown("**Đơn thuốc đã kê:**")
                    df_p = pd.DataFrame(pres)
                    df_p.rename(
                        columns={
                            "medicine_name": "Tên thuốc",
                            "dosage": "Hàm lượng",
                            "quantity": "Số lượng",
                            "usage": "Cách dùng",
                        },
                        inplace=True,
                    )
                    st.dataframe(df_p, use_container_width=True, hide_index=True)

        # Điều hướng phân trang
        render_pagination(
            total_items=total_matched_recs,
            page_size=rec_limit,
            session_key="record_page",
        )
    else:
        st.info("Không có bệnh án nào khớp với điều kiện tra cứu.", icon="ℹ️")

# ---------------------------------------------------------------------
# TAB 3: CẬP NHẬT BỆNH ÁN
# ---------------------------------------------------------------------
with tab_edit:
    st.subheader("Chỉnh Sửa Hồ Sơ Bệnh Án")

    search_rec_edit = st.text_input(
        "Tìm bệnh án cần sửa (Mã BA, Chẩn đoán)",
        placeholder="Nhập BA-2026-XXXX...",
        key="search_rec_edit_tab",
    )

    recs_to_edit, _ = api_get_records(
        skip=0,
        limit=50,
        search=search_rec_edit.strip() if search_rec_edit else None,
    )

    if recs_to_edit:
        rec_map = {
            f"{r.get('record_code')} - {DEPT_LABELS.get(r.get('department'), r.get('department'))} - {r.get('diagnosis', '')[:30]}": r
            for r in recs_to_edit
        }
        selected_rec_key = st.selectbox(
            "Chọn bệnh án cần sửa:",
            options=list(rec_map.keys()),
            key="select_rec_to_edit",
        )
        editing_record = rec_map[selected_rec_key]
        editing_rec_id = str(editing_record.get("_id") or editing_record.get("id"))

        with st.form("form_edit_record_workstation"):
            er_c1, er_c2 = st.columns(2)
            with er_c1:
                e_doc = st.text_input("Bác sĩ phụ trách *", value=editing_record.get("doctor_name", ""))
                e_sym = st.text_input("Triệu chứng *", value=editing_record.get("symptoms", ""))
            with er_c2:
                e_diag = st.text_input("Chẩn đoán *", value=editing_record.get("diagnosis", ""))
                e_follow = st.checkbox("Chỉ định tái khám", value=editing_record.get("follow_up_required", False))

            st.markdown(f"**Chuyên khoa:** {DEPT_LABELS.get(editing_record.get('department'), editing_record.get('department'))}")
            st.divider()

            submit_rec_edit = st.form_submit_button("Lưu Thay Đổi Bệnh Án", type="primary", use_container_width=True)

            if submit_rec_edit:
                if not e_doc or not e_sym or not e_diag:
                    st.error("Vui lòng điền đầy đủ Bác sĩ, Triệu chứng và Chẩn đoán.")
                else:
                    update_rec_payload = {
                        "doctor_name": e_doc.strip(),
                        "symptoms": e_sym.strip(),
                        "diagnosis": e_diag.strip(),
                        "follow_up_required": e_follow,
                    }

                    try:
                        res, status_code = api_update_record(editing_rec_id, update_rec_payload)
                        if status_code == 200:
                            st.success("Cập nhật bệnh án thành công!", icon="✅")
                            st.rerun()
                        else:
                            st.error(f"Lỗi phản hồi API: {res}")
                    except Exception as ex:
                        st.error(f"Lỗi khi cập nhật bệnh án: {ex}")
    else:
        st.info("Không tìm thấy bệnh án phù hợp để chỉnh sửa.", icon="ℹ️")

# ---------------------------------------------------------------------
# TAB 4: XÓA BỆNH ÁN
# ---------------------------------------------------------------------
with tab_delete:
    st.subheader("Xóa Hồ Sơ Bệnh Án")

    search_rec_del = st.text_input(
        "Tìm bệnh án cần xóa (Mã BA)",
        placeholder="Nhập BA-2026-XXXX...",
        key="search_rec_del_tab",
    )

    recs_to_del, _ = api_get_records(
        skip=0,
        limit=50,
        search=search_rec_del.strip() if search_rec_del else None,
    )

    if recs_to_del:
        rec_del_map = {
            f"{r.get('record_code')} - {DEPT_LABELS.get(r.get('department'), r.get('department'))} - {r.get('diagnosis', '')[:30]}": r
            for r in recs_to_del
        }
        selected_del_key = st.selectbox(
            "Chọn bệnh án cần xóa:",
            options=list(rec_del_map.keys()),
            key="select_rec_to_delete",
        )
        target_rec = rec_del_map[selected_del_key]
        target_rec_id = str(target_rec.get("_id") or target_rec.get("id"))

        st.error(
            f"Xác nhận xóa bệnh án: **{target_rec.get('record_code')}** (Khoa: {DEPT_LABELS.get(target_rec.get('department'))}). Thao tác này không thể hoàn tác.",
            icon="⚠️",
        )

        confirm_rec_del = st.checkbox("Tôi xác nhận muốn xóa vĩnh viễn hồ sơ bệnh án này khỏi MongoDB Atlas.")

        if st.button("Xác Nhận Xóa Bệnh Án", type="primary", disabled=not confirm_rec_del, use_container_width=True):
            try:
                status_code = api_delete_record(target_rec_id)
                if status_code in [200, 204]:
                    st.success(f"Đã xóa thành công bệnh án {target_rec.get('record_code')}!", icon="✅")
                    st.rerun()
                else:
                    st.error(f"Lỗi phản hồi API khi xóa (Mã: {status_code})")
            except Exception as ex:
                st.error(f"Lỗi khi xóa bệnh án: {ex}")
    else:
        st.info("Không tìm thấy bệnh án phù hợp để xóa.", icon="ℹ️")

# =====================================================================
# 6. FOOTER
# =====================================================================
render_workstation_footer()
