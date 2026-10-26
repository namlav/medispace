import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

from frontend.api_client import (
    api_get_patients, 
    api_get_records, 
    api_create_record, 
    api_update_record, 
    api_delete_record
)
DEPARTMENTS = ["TIM_MACH", "DA_LIEU", "RANG_HAM_MAT"]

st.set_page_config(page_title="Quản Lý Hồ Sơ Bệnh Án Động | MediSpace", page_icon="📋", layout="wide")

st.title("📋 Quản Lý Hồ Sơ Bệnh Án Động (RESTful API)")
st.caption("Khám bệnh, tra cứu, chỉnh sửa và xóa hồ sơ bệnh án thông qua FastAPI Backend")

tab_create, tab_search, tab_edit, tab_delete = st.tabs([
    "➕ Khám Bệnh & Lập Hồ Sơ Mới", 
    "🔍 Tra Cứu & Tìm Kiếm Bệnh Án",
    "✏️ Chỉnh Sửa Bệnh Án",
    "🗑️ Xóa Hồ Sơ Bệnh Án"
])

# Tải danh sách bệnh nhân qua API
try:
    all_patients, _ = api_get_patients(skip=0, limit=1000)
except Exception:
    st.error("Không kết nối được FastAPI Backend. Hãy kiểm tra backend đang chạy ở cổng 8000.")
    st.stop()
patient_map = {str(p.get("_id") or p.get("id")): p for p in all_patients}

# ==========================================
# TAB 1: KHÁM BỆNH & LẬP HỒ SƠ BỆNH ÁN MỚI
# ==========================================
with tab_create:
    if not all_patients:
        st.warning("Chưa có bệnh nhân nào trong hệ thống! Vui lòng tạo bệnh nhân trước.")
        st.stop()

    patient_options = {
        f"{p.get('patient_code')} - {p.get('full_name')} ({p.get('gender')}, {p.get('dob')})": str(p.get('_id') or p.get('id')) 
        for p in all_patients
    }

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
    )

    if all_recs:
        record_options_edit = {
            f"[{r.get('record_code')}] - BN: {patient_map.get(str(r.get('patient_id')), {}).get('patient_code', 'N/A')} - {patient_map.get(str(r.get('patient_id')), {}).get('full_name', 'N/A')} - Khoa: {r.get('department')}": str(r.get("_id") or r.get("id"))
            for r in all_recs
        }
        selected_label_edit = st.selectbox("Chọn hồ sơ bệnh án cần sửa:", options=list(record_options_edit.keys()), key="select_edit_rec_tab")
        chosen_rec_id = record_options_edit[selected_label_edit]
        
        editing_rec = next((r for r in all_recs if str(r.get("_id") or r.get("id")) == chosen_rec_id), None)
        if editing_rec:
            old_dept = editing_rec.get("department", "TIM_MACH")
            old_spec_data = editing_rec.get("specialty_data", {})
            
            st.markdown("### 1. Thông Tin Hành Chính & Thăm Khám")
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                e_rec_code = st.text_input("Mã phiếu khám *", value=editing_rec.get("record_code", ""), key="e_code_in")
                dept_list = DEPARTMENTS
                dept_idx = dept_list.index(old_dept) if old_dept in dept_list else 0
                
                selected_edit_dept = st.selectbox(
                    "Chuyên khoa khám *",
                    options=dept_list,
                    index=dept_idx,
                    format_func=lambda x: {
                        "TIM_MACH": "❤️ Khoa Tim Mạch",
                        "DA_LIEU": "🔬 Khoa Da Liễu",
                        "RANG_HAM_MAT": "🦷 Khoa Răng - Hàm - Mặt"
                    }.get(x, x),
                    key="select_edit_dept_box"
                )
                
            with col_e2:
                e_doc_name = st.text_input("Bác sĩ phụ trách *", value=editing_rec.get("doctor_name", ""), key="e_doc_in")
                e_symptoms = st.text_input("Lý do khám / Triệu chứng lâm sàng", value=editing_rec.get("symptoms", ""), key="e_symp_in")
                e_diagnosis = st.text_input("Chẩn đoán bệnh", value=editing_rec.get("diagnosis", ""), key="e_diag_in")

            st.markdown("---")
            st.subheader(f"🩺 Dữ Liệu Đặc Thù Của {selected_edit_dept} (Dynamic Schema)")
            
            updated_specialty_data = {}
            
            if selected_edit_dept == "TIM_MACH":
                bp = old_spec_data.get("blood_pressure", {})
                sys_val = bp.get("systolic", 140) if isinstance(bp, dict) else 140
                dia_val = bp.get("diastolic", 90) if isinstance(bp, dict) else 90
                
                tc1, tc2, tc3 = st.columns(3)
                with tc1:
                    systolic = st.number_input("Huyết áp tâm thu (mmHg):", min_value=60, max_value=250, value=int(sys_val), key="edit_tm_sys")
                    diastolic = st.number_input("Huyết áp tâm trương (mmHg):", min_value=40, max_value=150, value=int(dia_val), key="edit_tm_dia")
                with tc2:
                    heart_rate = st.number_input("Nhịp tim (lần/phút):", min_value=40, max_value=200, value=int(old_spec_data.get("heart_rate_bpm", 82)), key="edit_tm_hr")
                    ef = st.number_input("Chỉ số phân suất tống máu EF (%):", min_value=20, max_value=85, value=int(old_spec_data.get("ejection_fraction_ef", 58)), key="edit_tm_ef")
                with tc3:
                    ecg_opts = ["Nhịp xoang bình thường", "Nhịp xoang nhanh, ST chênh xuống nhẹ", "Ngoại tâm thu thất rải rác", "Phì đại thất trái"]
                    cur_ecg = old_spec_data.get("ecg_result", "Nhịp xoang bình thường")
                    ecg_idx = ecg_opts.index(cur_ecg) if cur_ecg in ecg_opts else 0
                    ecg = st.selectbox("Kết quả Điện tâm đồ (ECG):", ecg_opts, index=ecg_idx, key="edit_tm_ecg")
                    
                    risk_opts = ["Thấp", "Trung bình", "Cao", "Rất cao"]
                    cur_risk = old_spec_data.get("cardiovascular_risk", "Thấp")
                    risk_idx = risk_opts.index(cur_risk) if cur_risk in risk_opts else 0
                    risk = st.selectbox("Phân tầng nguy cơ tim mạch:", risk_opts, index=risk_idx, key="edit_tm_risk")
                    
                updated_specialty_data = {
                    "blood_pressure": {"systolic": systolic, "diastolic": diastolic},
                    "heart_rate_bpm": heart_rate,
                    "ejection_fraction_ef": ef,
                    "ecg_result": ecg,
                    "cardiovascular_risk": risk
                }

            elif selected_edit_dept == "DA_LIEU":
                dc1, dc2 = st.columns(2)
                with dc1:
                    loc_opts = ["Khuôn mặt", "Cẳng tay", "Bàn tay", "Lưng", "Vùng ngực", "Da đầu", "Cẳng chân"]
                    cur_locs = old_spec_data.get("lesion_locations", ["Cẳng tay"])
                    valid_locs = [l for l in cur_locs if l in loc_opts] if isinstance(cur_locs, list) else ["Cẳng tay"]
                    locations = st.multiselect("Vị trí tổn thương da:", loc_opts, default=valid_locs if valid_locs else ["Cẳng tay"], key="edit_dl_loc")
                    
                    les_opts = ["Mảng hồng ban giới hạn rõ", "Sẩn viêm, mụn mủ hoại tử", "Mụn nước mọc thành chùm rải rác", "Vảy nến bong tróc màu bạc", "Mảng thâm sạm tăng sắc tố"]
                    cur_les = old_spec_data.get("lesion_type", "Mảng hồng ban giới hạn rõ")
                    les_idx = les_opts.index(cur_les) if cur_les in les_opts else 0
                    lesion_type = st.selectbox("Loại thương tổn đặc trưng:", les_opts, index=les_idx, key="edit_dl_les")
                with dc2:
                    pru_opts = ["Không ngứa (0)", "Nhẹ (2/10)", "Trung bình (5/10)", "Nặng (8/10)", "Dữ dội (10/10)"]
                    cur_pru = old_spec_data.get("pruritus_level", "Trung bình (5/10)")
                    pruritus = st.select_slider("Mức độ ngứa:", options=pru_opts, value=cur_pru if cur_pru in pru_opts else "Trung bình (5/10)", key="edit_dl_pru")
                    
                    patch_test = st.text_input("Kết quả xét nghiệm áp bì (Patch test):", value=old_spec_data.get("patch_test", "Âm tính"), key="edit_dl_patch")
                    is_contagious = st.checkbox("Có nguy cơ lây nhiễm sang người khác", value=bool(old_spec_data.get("is_contagious", False)), key="edit_dl_con")
                    
                updated_specialty_data = {
                    "lesion_locations": locations,
                    "lesion_type": lesion_type,
                    "pruritus_level": pruritus,
                    "patch_test": patch_test,
                    "is_contagious": is_contagious
                }

            elif selected_edit_dept == "RANG_HAM_MAT":
                chart = old_spec_data.get("dental_chart", [])
                default_teeth_str = ", ".join([str(t.get("tooth_number")) for t in chart]) if chart else "36, 46"
                
                c1, c2 = st.columns(2)
                with c1:
                    tooth_input = st.text_input("Vị trí răng tổn thương (cách nhau dấu phẩy, VD: 36, 46):", value=default_teeth_str, key="edit_rhm_teeth")
                    
                    cond_opts = ["Sâu ngà buốt tủy", "Sâu men răng nhẹ", "Vỡ mẻ thân răng", "Răng khôn mọc lệch đâm R lân cận"]
                    cur_cond = chart[0].get("condition", "Sâu ngà buốt tủy") if chart else "Sâu ngà buốt tủy"
                    cond_idx = cond_opts.index(cur_cond) if cur_cond in cond_opts else 0
                    tooth_cond = st.selectbox("Tình trạng tổn thương răng:", cond_opts, index=cond_idx, key="edit_rhm_cond")
                    
                    treat_opts = ["Hàn trám composite", "Điều trị tủy phục hồi", "Chỉ định nhổ bỏ", "Cắt lợi trùm"]
                    cur_treat = chart[0].get("treatment", "Hàn trám composite") if chart else "Hàn trám composite"
                    treat_idx = treat_opts.index(cur_treat) if cur_treat in treat_opts else 0
                    tooth_treatment = st.selectbox("Hướng điều trị:", treat_opts, index=treat_idx, key="edit_rhm_treat")
                with c2:
                    tartar = st.slider("Mức độ cao răng (Tartar Grade 0-3):", min_value=0, max_value=3, value=int(old_spec_data.get("tartar_grade", 2)), key="edit_rhm_tar")
                    gingivitis = st.checkbox("Có viêm nướu / Chảy máu chân răng", value=bool(old_spec_data.get("gingivitis", True)), key="edit_rhm_ging")
                    
                    hyg_opts = ["Kém", "Trung bình", "Tốt"]
                    cur_hyg = old_spec_data.get("oral_hygiene_score", "Trung bình")
                    hyg_idx = hyg_opts.index(cur_hyg) if cur_hyg in hyg_opts else 1
                    hygiene = st.selectbox("Đánh giá vệ sinh răng miệng:", hyg_opts, index=hyg_idx, key="edit_rhm_hyg")
                    
                teeth_list = [int(t.strip()) for t in tooth_input.split(",") if t.strip().isdigit()]
                updated_specialty_data = {
                    "dental_chart": [{"tooth_number": t, "condition": tooth_cond, "treatment": tooth_treatment} for t in teeth_list],
                    "tartar_grade": tartar,
                    "gingivitis": gingivitis,
                    "oral_hygiene_score": hygiene
                }

            st.markdown("---")
            e_follow_up = st.checkbox("Yêu cầu hẹn tái khám", value=bool(editing_rec.get("follow_up_required", False)), key="e_follow_chk")
            
            if st.button("💾 Lưu Cập Nhật Bệnh Án", type="primary", width="stretch", key="btn_update_rec"):
                update_payload = {
                    "record_code": e_rec_code,
                    "department": selected_edit_dept,
                    "doctor_name": e_doc_name,
                    "symptoms": e_symptoms,
                    "diagnosis": e_diagnosis,
                    "specialty_data": updated_specialty_data,
                    "follow_up_required": e_follow_up
                }
                try:
                    res, status_code = api_update_record(chosen_rec_id, update_payload)
                    if status_code == 200:
                        st.toast("Cập nhật thành công hồ sơ bệnh án và dữ liệu đặc thù!", icon="✅")
                        st.success("Cập nhật thành công hồ sơ bệnh án và dữ liệu đặc thù!")
                        st.rerun()
                    else:
                        st.error(f"Lỗi từ API: {res}")
                except Exception as e:
                    st.error(f"Lỗi khi cập nhật bệnh án: {e}")
    else:
        st.warning("Không tìm thấy hồ sơ bệnh án nào để chỉnh sửa.")

# ==========================================
# TAB 4: XÓA HỒ SƠ BỆNH ÁN
# ==========================================
with tab_delete:
    st.subheader("🗑️ Xóa Hồ Sơ Bệnh Án")
    search_del = st.text_input("🔍 Tìm bệnh án cần xóa (Mã BA, Mã BN, Tên BN):", key="search_del_rec_tab")
    recs_del, _ = api_get_records(
        skip=0,
        limit=1000,
        search=search_del.strip() or None
    )

    if recs_del:
        record_options_del = {
            f"[{r.get('record_code')}] - BN: {patient_map.get(str(r.get('patient_id')), {}).get('patient_code', 'N/A')} - {patient_map.get(str(r.get('patient_id')), {}).get('full_name', 'N/A')} - Khoa: {r.get('department')}": str(r.get("_id") or r.get("id"))
            for r in recs_del
        }
        selected_label_del = st.selectbox("Chọn hồ sơ bệnh án cần xóa:", options=list(record_options_del.keys()), key="select_del_rec_tab")
        chosen_del_rec_id = record_options_del[selected_label_del]
        
        target_rec = next((r for r in recs_del if str(r.get("_id") or r.get("id")) == chosen_del_rec_id), None)
        if target_rec:
            st.warning(f"⚠️ Bạn có chắc chắn muốn xóa vĩnh viễn phiếu khám mã **{target_rec.get('record_code')}** của bệnh nhân **{patient_map.get(str(target_rec.get('patient_id')), {}).get('full_name', 'N/A')}** không?")
            if st.button("🗑️ Xác Nhận Xóa Vĩnh Viễn Bệnh Án", type="primary"):
                try:
                    status_code = api_delete_record(chosen_del_rec_id)
                    if status_code in [200, 204]:
                        st.toast("Đã xóa hồ sơ bệnh án thành công!", icon="🗑️")
                        st.success("Đã xóa hồ sơ bệnh án thành công!")
                        st.rerun()
                    else:
                        st.error(f"Lỗi khi xóa qua API, mã lỗi: {status_code}")
                except Exception as e:
                    st.error(f"Lỗi khi xóa bệnh án: {e}")
    else:
        st.warning("Không tìm thấy hồ sơ bệnh án phù hợp để xóa.")