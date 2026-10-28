import re
import sys
from pathlib import Path
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
    api_create_patient,
    api_update_patient,
    api_delete_patient,
    api_get_records,
    api_get_next_patient_code,
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
    validate_patient_name,
)

st.set_page_config(
    page_title="MediSpace | Hồ Sơ Bệnh Nhân",
    page_icon="👤",
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
    _, total_all = api_get_patients(skip=0, limit=1)
except Exception:
    st.error("Không kết nối được FastAPI Backend. Vui lòng kiểm tra cổng 8000.", icon="⚠️")
    st.stop()

# =====================================================================
# 3. HEADER WORKSTATION (OCEANIC BLUE)
# =====================================================================
render_workstation_header(
    title="Tiếp Đón & Quản Lý Hồ Sơ Bệnh Nhân",
    subtitle="Định danh bệnh nhân, quản lý thông tin hành chính, tiền sử dị ứng và dòng thời gian điều trị",
    badge_label=f"{format_number(total_all)} HỒ SƠ ĐỊNH DANH",
    badge_status="live",
    icon_name="patient",
)

# =====================================================================
# 4. CHỈ SỐ LÂM SÀNG TỔNG QUAN (3 CỘT)
# =====================================================================
kp1, kp2, kp3 = st.columns(3)

with kp1:
    render_kpi_card(
        label="Tổng Số Bệnh Nhân",
        value=format_number(total_all),
        foot="Hồ sơ đã được cấp mã BN",
        icon_name="patient",
        accent_color="#0284C7",
    )

with kp2:
    render_kpi_card(
        label="Quy Chuẩn Định Danh",
        value="BN-XXXX",
        foot="Khóa định danh trong collection patients",
        icon_name="shield",
        accent_color="#0369A1",
    )

with kp3:
    render_kpi_card(
        label="Đồng Bộ Bệnh Án",
        value="Single-Read",
        foot="Mảng đơn thuốc nhúng & liên kết 1-N",
        icon_name="database",
        accent_color="#075985",
    )

st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

# =====================================================================
# 5. CÁC PHÂN VÙNG CHỨC NĂNG (TABS)
# =====================================================================
tab_list, tab_detail, tab_create, tab_edit, tab_delete = st.tabs(
    [
        "Danh Sách Bệnh Nhân",
        "Hồ Sơ & Lịch Sử Khám",
        "Tiếp Nhận Bệnh Nhân Mới",
        "Chỉnh Sửa Thông Tin",
        "Xóa Hồ Sơ",
    ]
)

# ---------------------------------------------------------------------
# TAB 1: DANH SÁCH BỆNH NHÂN (PHÂN TRANG TỐI ĐA 50 HỒ SƠ/TRANG)
# ---------------------------------------------------------------------
with tab_list:
    st.subheader("Tra Cứu Hồ Sơ Bệnh Nhân")

    c_search, c_limit = st.columns([3, 1])
    with c_search:
        search_query = st.text_input(
            "Tìm kiếm theo mã số BN, họ tên hoặc số điện thoại",
            placeholder="Ví dụ: BN-0001, Nguyễn Văn An, 0912...",
            key="search_input_list",
        )
    with c_limit:
        limit_val = st.selectbox(
            "Số lượng mỗi trang (tối đa 50)",
            options=[10, 20, 50],
            index=2,
            key="limit_select_list",
        )

    # Đặt lại về trang 1 khi đổi từ khóa tìm kiếm hoặc cỡ trang
    curr_search_term = search_query.strip() if search_query else ""
    if (
        st.session_state.get("bn_last_search") != curr_search_term
        or st.session_state.get("bn_last_limit") != limit_val
    ):
        st.session_state["bn_last_search"] = curr_search_term
        st.session_state["bn_last_limit"] = limit_val
        st.session_state["patient_page"] = 1
        st.session_state["patient_page_jump_txt"] = "1"

    if "patient_page" not in st.session_state:
        st.session_state["patient_page"] = 1

    current_page = st.session_state["patient_page"]
    skip_val = (current_page - 1) * limit_val

    patients, total_matched = api_get_patients(
        skip=skip_val,
        limit=limit_val,
        search=curr_search_term if curr_search_term else None,
    )

    total_pages = max(1, (total_matched + limit_val - 1) // limit_val)
    if current_page > total_pages:
        st.session_state["patient_page"] = total_pages
        current_page = total_pages
        skip_val = (current_page - 1) * limit_val
        patients, total_matched = api_get_patients(
            skip=skip_val,
            limit=limit_val,
            search=curr_search_term if curr_search_term else None,
        )

    start_idx = skip_val + 1 if total_matched > 0 else 0
    end_idx = min(skip_val + len(patients), total_matched)

    st.markdown(
        f"""
        <div style="font-size: 0.85rem; color: var(--ms-text-muted); margin-bottom: 0.75rem;">
            Hiển thị hồ sơ <strong>{start_idx} - {end_idx}</strong> trên tổng số <strong>{format_number(total_matched)}</strong> hồ sơ phù hợp · Trang <strong>{current_page}/{total_pages}</strong>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if patients:
        table_rows = []
        for p in patients:
            table_rows.append(
                {
                    "Mã BN": p.get("patient_code", "—"),
                    "Họ và Tên": p.get("full_name", "—"),
                    "Ngày sinh": p.get("dob", "—"),
                    "Giới tính": p.get("gender", "—"),
                    "Số điện thoại": p.get("phone", "—"),
                    "Nhóm máu": p.get("blood_group") or "—",
                    "Tiền sử dị ứng": (
                        ", ".join(p.get("allergies", []))
                        if p.get("allergies")
                        else "Không"
                    ),
                    "Địa chỉ": p.get("address") or "—",
                }
            )
        df_patients = pd.DataFrame(table_rows)
        st.dataframe(
            df_patients,
            use_container_width=True,
            hide_index=True,
            height=480,
        )

        # Điều hướng phân trang
        render_pagination(
            total_items=total_matched,
            page_size=limit_val,
            session_key="patient_page",
        )
    else:
        st.info("Không tìm thấy hồ sơ bệnh nhân nào khớp với tiêu chí tìm kiếm.", icon="ℹ️")

# ---------------------------------------------------------------------
# TAB 2: HỒ SƠ CHI TIẾT & LỊCH SỬ KHÁM
# ---------------------------------------------------------------------
with tab_detail:
    st.subheader("Hồ Sơ Lâm Sàng & Lịch Sử Các Lần Khám")

    search_detail = st.text_input(
        "Tìm bệnh nhân để xem bệnh án (Mã BN, Họ tên, SĐT)",
        placeholder="Nhập thông tin bệnh nhân...",
        key="search_patient_detail",
    )

    patients_detail, _ = api_get_patients(
        skip=0,
        limit=50,
        search=search_detail.strip() if search_detail else None,
    )

    if patients_detail:
        patient_map = {
            f"{p.get('patient_code')} - {p.get('full_name')} ({p.get('phone', 'Không có SĐT')})": p
            for p in patients_detail
        }
        selected_key = st.selectbox(
            "Chọn bệnh nhân:",
            options=list(patient_map.keys()),
            key="select_patient_dossier",
        )
        chosen_patient = patient_map[selected_key]
        chosen_id = str(chosen_patient.get("_id") or chosen_patient.get("id"))

        # Banner tóm tắt bệnh nhân
        allergies_str = (
            ", ".join(chosen_patient.get("allergies", []))
            if chosen_patient.get("allergies")
            else "Không ghi nhận"
        )
        st.markdown(
            f"""
            <div class="ms-patient-banner">
                <div class="ms-patient-info">
                    <div>
                        <div style="font-size: 0.8rem; color: var(--ms-text-muted); text-transform: uppercase; font-weight: 700;">Hồ sơ bệnh nhân</div>
                        <div class="ms-patient-name">{escape(str(chosen_patient.get("full_name")))}</div>
                    </div>
                    <span class="ms-code-badge">{escape(str(chosen_patient.get("patient_code")))}</span>
                </div>
                <div class="ms-patient-vitals">
                    <span class="ms-vital-tag">Ngày sinh: <strong>{chosen_patient.get("dob")}</strong></span>
                    <span class="ms-vital-tag">Giới tính: <strong>{chosen_patient.get("gender")}</strong></span>
                    <span class="ms-vital-tag">Nhóm máu: <strong>{chosen_patient.get("blood_group") or "Chưa rõ"}</strong></span>
                    <span class="ms-vital-tag">SĐT: <strong>{chosen_patient.get("phone") or "—"}</strong></span>
                    <span class="ms-vital-tag" style="background: var(--ms-triage-amber-bg); border-color: var(--ms-triage-amber-border); color: var(--ms-triage-amber);">Dị ứng: <strong>{escape(allergies_str)}</strong></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Lấy lịch sử bệnh án của bệnh nhân này
        try:
            records, total_recs = api_get_records(patient_id=chosen_id, limit=100)
            st.markdown(f"##### Lịch Sử Điều Trị ({total_recs} lần khám)")

            if records:
                for rec in records:
                    dept_badge = rec.get("department", "CHUYÊN KHOA")
                    with st.expander(
                        f"Mã BA: {rec.get('record_code', '—')} · {dept_badge} · Khám ngày: {rec.get('visit_date', '')[:10]} · BS: {rec.get('doctor_name', '—')}",
                        expanded=False,
                    ):
                        c_info1, c_info2 = st.columns(2)
                        with c_info1:
                            st.markdown(f"**Triệu chứng:** {rec.get('symptoms', '—')}")
                            st.markdown(f"**Chẩn đoán:** {rec.get('diagnosis', '—')}")
                        with c_info2:
                            st.markdown(f"**Tái khám:** {'Có' if rec.get('follow_up_required') else 'Không'}")
                            if rec.get("follow_up_date"):
                                st.markdown(f"**Ngày hẹn tái khám:** {rec.get('follow_up_date')[:10]}")

                        spec_data = rec.get("specialty_data", {})
                        if spec_data:
                            st.markdown("**Thông số lâm sàng chuyên khoa:**")
                            st.json(spec_data)

                        prescriptions = rec.get("prescriptions", [])
                        if prescriptions:
                            st.markdown("**Đơn thuốc đã kê:**")
                            df_pres = pd.DataFrame(prescriptions)
                            df_pres.rename(
                                columns={
                                    "medicine_name": "Tên thuốc",
                                    "dosage": "Hàm lượng",
                                    "quantity": "Số lượng",
                                    "usage": "Cách dùng",
                                },
                                inplace=True,
                            )
                            st.dataframe(df_pres, use_container_width=True, hide_index=True)
            else:
                st.info("Bệnh nhân này chưa có lượt khám bệnh nào được lưu trong hệ thống.", icon="ℹ️")
        except Exception as e:
            st.warning(f"Không thể tải lịch sử bệnh án: {e}")
    else:
        st.info("Không có bệnh nhân phù hợp để xem hồ sơ.", icon="ℹ️")

# ---------------------------------------------------------------------
# TAB 3: TIẾP NHẬN BỆNH NHÂN MỚI (MÃ TỰ ĐỘNG TĂNG & RÀNG BUỘC HỌ TÊN)
# ---------------------------------------------------------------------
with tab_create:
    st.subheader("Đăng Ký Hồ Sơ Bệnh Nhân Mới")

    auto_next_code = api_get_next_patient_code() or (
        f"BN-{total_all + 1:04d}" if total_all < 9999 else f"BN-{total_all + 1:05d}"
    )

    with st.form("form_create_patient_workstation"):
        c1, c2 = st.columns(2, gap="large")

        with c1:
            p_code = st.text_input(
                "Mã bệnh nhân (Tự động cấp tăng dần) *",
                value=auto_next_code,
                disabled=True,
                help="Mã bệnh nhân được hệ thống cấp tự động tăng theo hồ sơ cuối cùng + 1.",
            )
            raw_p_name = st.text_input(
                "Họ và tên bệnh nhân *",
                placeholder="Ví dụ: Nguyễn Văn An",
                help="Họ tên phải hợp lệ (tiếng Việt/Latin), không chứa chữ số, ký tự đặc biệt hoặc spam ký tự.",
            )
            p_dob = st.date_input("Ngày sinh")
            p_gender = st.selectbox("Giới tính *", ["Nam", "Nữ", "Khác"])

        with c2:
            col_prefix, col_phone = st.columns([1, 3])
            with col_prefix:
                st.text_input("Quốc gia", value="+84", disabled=True)
            with col_phone:
                p_phone_suffix = st.text_input(
                    "Số điện thoại (bỏ số 0 đầu) *",
                    placeholder="912345678",
                    max_chars=10,
                )
            p_blood = st.selectbox(
                "Nhóm máu",
                ["Chưa xác định", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"],
            )
            p_allergies = st.text_input(
                "Tiền sử dị ứng thuốc / thức ăn (cách nhau bởi dấu phẩy)",
                placeholder="Ví dụ: Penicillin, Aspirin, Hải sản...",
            )
            p_address = st.text_input("Địa chỉ thường trú", placeholder="Số nhà, đường, quận/huyện, tỉnh/TP")

        st.divider()
        submitted = st.form_submit_button("Lưu Hồ Sơ Bệnh Nhân", type="primary", use_container_width=True)

        if submitted:
            cleaned_name = raw_p_name.strip()
            phone_body = p_phone_suffix.strip()
            if phone_body.startswith("0"):
                phone_body = phone_body[1:]

            is_valid_name, err_name = validate_patient_name(cleaned_name)

            if not p_code or not cleaned_name:
                st.error("Vui lòng điền đầy đủ thông tin Họ và tên bệnh nhân.", icon="⚠️")
            elif not is_valid_name:
                st.error(f"Tên bệnh nhân không hợp lệ: {err_name}", icon="⚠️")
            elif not phone_body.isdigit() or not (9 <= len(phone_body) <= 10):
                st.error("Số điện thoại không hợp lệ (cần 9-10 chữ số).", icon="⚠️")
            else:
                full_phone = f"+84{phone_body}"
                formatted_name = cleaned_name.title()
                allergies_list = [a.strip() for a in p_allergies.split(",") if a.strip()] if p_allergies else []

                new_patient = {
                    "patient_code": p_code,
                    "full_name": formatted_name,
                    "dob": str(p_dob),
                    "gender": p_gender,
                    "phone": full_phone,
                    "address": p_address,
                    "blood_group": p_blood if p_blood != "Chưa xác định" else None,
                    "allergies": allergies_list,
                }

                try:
                    res, status_code = api_create_patient(new_patient)
                    if status_code in [200, 201]:
                        st.success(f"Tiếp nhận bệnh nhân thành công! Mã BN: {p_code} - {formatted_name}", icon="✅")
                        st.rerun()
                    else:
                        st.error(f"Lỗi phản hồi từ API Backend: {res}")
                except Exception as ex:
                    st.error(f"Lỗi kết nối khi tạo bệnh nhân: {ex}")

# ---------------------------------------------------------------------
# TAB 4: CHỈNH SỬA THÔNG TIN BỆNH NHÂN
# ---------------------------------------------------------------------
with tab_edit:
    st.subheader("Chỉnh Sửa Thông Tin Hành Chính Bệnh Nhân")

    search_edit = st.text_input(
        "Tìm kiếm bệnh nhân cần chỉnh sửa",
        placeholder="Nhập Mã BN, họ tên hoặc SĐT...",
        key="search_edit_patient",
    )

    patients_edit, _ = api_get_patients(
        skip=0,
        limit=50,
        search=search_edit.strip() if search_edit else None,
    )

    if patients_edit:
        patient_options_edit = {
            f"{p.get('patient_code')} - {p.get('full_name')} ({p.get('phone', 'Không SĐT')})": str(
                p.get("_id") or p.get("id")
            )
            for p in patients_edit
        }
        selected_label_edit = st.selectbox(
            "Chọn bệnh nhân cần cập nhật:",
            options=list(patient_options_edit.keys()),
            key="select_edit_patient",
        )
        chosen_id_edit = patient_options_edit[selected_label_edit]
        editing_p = next(
            (p for p in patients_edit if str(p.get("_id") or p.get("id")) == chosen_id_edit),
            None,
        )

        if editing_p:
            old_phone = editing_p.get("phone", "")
            if old_phone.startswith("+84"):
                old_phone_suffix = old_phone[3:]
            elif old_phone.startswith("0"):
                old_phone_suffix = old_phone[1:]
            else:
                old_phone_suffix = old_phone

            with st.form("form_edit_patient_workstation"):
                ec1, ec2 = st.columns(2, gap="large")
                with ec1:
                    e_code = st.text_input(
                        "Mã bệnh nhân (Cố định, không chỉnh sửa) *",
                        value=editing_p.get("patient_code", ""),
                        disabled=True,
                        help="Mã bệnh nhân do hệ thống tự sinh và không được phép thay đổi.",
                    )
                    raw_e_name = st.text_input("Họ và tên *", value=editing_p.get("full_name", ""))
                    try:
                        default_dob = pd.to_datetime(editing_p.get("dob")).date()
                    except Exception:
                        default_dob = pd.to_datetime("2000-01-01").date()
                    e_dob = st.date_input("Ngày sinh", value=default_dob)
                    gender_opts = ["Nam", "Nữ", "Khác"]
                    g_idx = gender_opts.index(editing_p.get("gender")) if editing_p.get("gender") in gender_opts else 0
                    e_gender = st.selectbox("Giới tính *", gender_opts, index=g_idx)

                with ec2:
                    col_eprefix, col_ephone = st.columns([1, 3])
                    with col_eprefix:
                        st.text_input("Quốc gia", value="+84", disabled=True, key="edit_prefix")
                    with col_ephone:
                        e_phone_suffix = st.text_input(
                            "Số điện thoại (bỏ số 0 đầu) *",
                            value=old_phone_suffix,
                            max_chars=10,
                        )
                    blood_opts = ["Chưa xác định", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
                    b_val = editing_p.get("blood_group") if editing_p.get("blood_group") in blood_opts else "Chưa xác định"
                    e_blood = st.selectbox("Nhóm máu", blood_opts, index=blood_opts.index(b_val))
                    allergies_val = ", ".join(editing_p.get("allergies", [])) if editing_p.get("allergies") else ""
                    e_allergies = st.text_input("Tiền sử dị ứng", value=allergies_val)
                    e_address = st.text_input("Địa chỉ thường trú", value=editing_p.get("address", ""))

                st.divider()
                submitted_update = st.form_submit_button("Lưu Thay Đổi", type="primary", use_container_width=True)

                if submitted_update:
                    cleaned_e_name = raw_e_name.strip()
                    e_phone_body = e_phone_suffix.strip()
                    if e_phone_body.startswith("0"):
                        e_phone_body = e_phone_body[1:]

                    is_valid_e_name, err_e_name = validate_patient_name(cleaned_e_name)

                    if not e_code or not cleaned_e_name:
                        st.error("Vui lòng điền đầy đủ Mã bệnh nhân và Họ tên.", icon="⚠️")
                    elif not is_valid_e_name:
                        st.error(f"Họ tên chỉnh sửa không hợp lệ: {err_e_name}", icon="⚠️")
                    elif not e_phone_body.isdigit() or not (9 <= len(e_phone_body) <= 10):
                        st.error("Số điện thoại không hợp lệ (cần 9-10 chữ số).", icon="⚠️")
                    else:
                        full_e_phone = f"+84{e_phone_body}"
                        formatted_e_name = cleaned_e_name.title()
                        allergies_list = [a.strip() for a in e_allergies.split(",") if a.strip()] if e_allergies else []

                        update_data = {
                            "patient_code": e_code,
                            "full_name": formatted_e_name,
                            "dob": str(e_dob),
                            "gender": e_gender,
                            "phone": full_e_phone,
                            "address": e_address,
                            "blood_group": e_blood if e_blood != "Chưa xác định" else None,
                            "allergies": allergies_list,
                        }

                        try:
                            res, status_code = api_update_patient(chosen_id_edit, update_data)
                            if status_code == 200:
                                st.success("Cập nhật thông tin hồ sơ bệnh nhân thành công!", icon="✅")
                                st.rerun()
                            else:
                                st.error(f"Lỗi phản hồi API: {res}")
                        except Exception as ex:
                            st.error(f"Lỗi khi cập nhật bệnh nhân: {ex}")
    else:
        st.info("Không tìm thấy bệnh nhân phù hợp để chỉnh sửa.", icon="ℹ️")

# ---------------------------------------------------------------------
# TAB 5: XÓA HỒ SƠ BỆNH NHÂN (SAFE DELETION)
# ---------------------------------------------------------------------
with tab_delete:
    st.subheader("Xóa Hồ Sơ Bệnh Nhân Khỏi Hệ Thống")

    st.markdown(
        """
        <div style="background: var(--ms-triage-red-bg); border: 1px solid var(--ms-triage-red-border); border-radius: var(--ms-radius-md); padding: 1rem 1.25rem; margin-bottom: 1rem;">
            <strong style="color: var(--ms-triage-red);">LƯU Ý QUAN TRỌNG:</strong>
            <span style="font-size: 0.88rem; color: var(--ms-text-body);">
                Thao tác xóa bệnh nhân sẽ đồng thời xóa vĩnh viễn toàn bộ các hồ sơ bệnh án liên quan của bệnh nhân này trong cơ sở dữ liệu MongoDB.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    search_del = st.text_input(
        "Tìm kiếm hồ sơ cần xóa (Mã BN, Họ tên, SĐT)",
        placeholder="Nhập thông tin bệnh nhân cần xóa...",
        key="search_del_patient",
    )

    patients_del, _ = api_get_patients(
        skip=0,
        limit=50,
        search=search_del.strip() if search_del else None,
    )

    if patients_del:
        patient_options_del = {
            f"{p.get('patient_code')} - {p.get('full_name')} ({p.get('phone', 'Không SĐT')})": str(
                p.get("_id") or p.get("id")
            )
            for p in patients_del
        }
        selected_label_del = st.selectbox(
            "Chọn bệnh nhân xác nhận xóa:",
            options=list(patient_options_del.keys()),
            key="select_del_patient",
        )
        chosen_id_del = patient_options_del[selected_label_del]
        target_p = next(
            (p for p in patients_del if str(p.get("_id") or p.get("id")) == chosen_id_del),
            None,
        )

        if target_p:
            st.error(
                f"Xác nhận xóa bệnh nhân: **{target_p.get('full_name')}** (Mã: `{target_p.get('patient_code')}`).",
                icon="⚠️",
            )

            confirm_del = st.checkbox("Tôi hiểu rằng dữ liệu và các bệnh án liên quan sẽ bị xóa vĩnh viễn khỏi MongoDB Atlas.")

            if st.button("Xác Nhận Xóa Vĩnh Viễn", type="primary", disabled=not confirm_del, use_container_width=True):
                try:
                    status_code = api_delete_patient(chosen_id_del)
                    if status_code in [200, 204]:
                        st.success(f"Đã xóa thành công hồ sơ bệnh nhân {target_p.get('full_name')}!", icon="✅")
                        st.rerun()
                    else:
                        st.error(f"Lỗi phản hồi API khi xóa (Mã: {status_code})")
                except Exception as ex:
                    st.error(f"Lỗi kết nối khi xóa: {ex}")
    else:
        st.info("Không có bệnh nhân phù hợp để xóa.", icon="ℹ️")

# =====================================================================
# 6. FOOTER
# =====================================================================
render_workstation_footer()
