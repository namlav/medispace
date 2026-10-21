import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import re

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

from frontend.api_client import (
    api_get_patients, 
    api_create_patient, 
    api_update_patient, 
    api_delete_patient,
    api_get_records,
    api_delete_record
)

st.set_page_config(page_title="Quản Lý Bệnh Nhân | MediSpace", page_icon="👤", layout="wide")

st.title("👤 Quản Lý Hồ Sơ Bệnh Nhân (RESTful API)")
st.caption("Quản lý thông tin hành chính bệnh nhân thông qua FastAPI Backend")

tab_list, tab_create, tab_edit, tab_delete = st.tabs([
    "📋 Danh Sách Bệnh Nhân", 
    "➕ Thêm Bệnh Nhân Mới", 
    "✏️ Chỉnh Sửa Bệnh Nhân", 
    "🗑️ Xóa Bệnh Nhân"
])

# Lấy tổng số lượng để gợi ý mã bệnh nhân mới
_, total_all = api_get_patients(skip=0, limit=1000)

# --- TAB 1: DANH SÁCH ---
with tab_list:
    c_search, c_limit = st.columns([3, 1])
    with c_search:
        search_query = st.text_input("🔍 Tìm kiếm theo Họ tên, Mã bệnh nhân hoặc Số điện thoại:", key="search_tab_1")
    with c_limit:
        limit_val = st.selectbox("Hiển thị tối đa:", [100, 200, 500, "Tất cả"], index=1)
        actual_limit = 10000 if limit_val == "Tất cả" else limit_val

    patients, total = api_get_patients(skip=0, limit=actual_limit, search=search_query if search_query else None)
    
    st.write(f"Hiển thị **{len(patients)}** / **{total}** hồ sơ bệnh nhân:")
    
    if patients:
        table_data = []
        for p in patients:
            table_data.append({
                "ID Hệ Thống": str(p.get("_id") or p.get("id")),
                "Mã BN": p.get("patient_code"),
                "Họ và Tên": p.get("full_name"),
                "Ngày sinh": p.get("dob"),
                "Giới tính": p.get("gender"),
                "Điện thoại": p.get("phone"),
                "Nhóm máu": p.get("blood_group"),
                "Dị ứng": ", ".join(p.get("allergies", [])) if p.get("allergies") else "Không",
                "Địa chỉ": p.get("address")
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(
            df.drop(columns=["ID Hệ Thống"]), 
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Chưa có hồ sơ bệnh nhân nào hoặc không tìm thấy kết quả phù hợp.")

# --- TAB 2: THÊM MỚI ---
with tab_create:
    st.subheader("Tạo Hồ Sơ Bệnh Nhân Mới")
    with st.form("form_create_patient"):
        c1, c2 = st.columns(2)
        with c1:
            p_code = st.text_input("Mã bệnh nhân *", value=f"BN-{total_all + 1:04d}")
            raw_p_name = st.text_input("Họ và tên *", placeholder="Ví dụ: Nguyễn Văn An")
            p_dob = st.date_input("Ngày sinh")
            p_gender = st.selectbox("Giới tính *", ["Nam", "Nữ", "Khác"])
        with c2:
            col_code, col_num = st.columns([1, 3])
            with col_code:
                st.text_input("Mã quốc gia", value="+84", disabled=True, key="prefix_add")
            with col_num:
                p_phone_suffix = st.text_input("Số điện thoại (không cần nhập số 0 ở đầu) *", placeholder="912345678", max_chars=10)
            
            p_blood = st.selectbox("Nhóm máu", ["Chưa xác định", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
            p_allergies = st.text_input("Dị ứng (cách nhau bởi dấu phẩy)", placeholder="Ví dụ: Penicillin, Hải sản")
            p_address = st.text_input("Địa chỉ thường trú", placeholder="Số nhà, đường, quận/huyện, tỉnh/TP")
            
        submitted = st.form_submit_button("💾 Lưu Hồ Sơ Bệnh Nhân")
        if submitted:
            cleaned_name = raw_p_name.strip()
            phone_body = p_phone_suffix.strip()
            if phone_body.startswith("0"):
                phone_body = phone_body[1:]

            vietnamese_name_regex = r"^[a-zA-ZàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵĐđ\s]+$"
            
            if not p_code or not cleaned_name:
                st.error("Vui lòng điền đầy đủ Mã bệnh nhân và Họ tên.")
            elif not re.match(vietnamese_name_regex, cleaned_name):
                st.error("❌ Họ và tên chỉ được chứa chữ cái, không được nhập số hoặc ký tự đặc biệt!")
            elif not phone_body.isdigit() or not (9 <= len(phone_body) <= 10):
                st.error("❌ Số điện thoại không hợp lệ! Chỉ được nhập số (9-10 chữ số tiếp theo sau +84).")
            else:
                full_phone = f"+84{phone_body}"
                formatted_name = cleaned_name.title()
                try:
                    allergies_list = [a.strip() for a in p_allergies.split(",") if a.strip()] if p_allergies else []
                    new_patient_data = {
                        "patient_code": p_code,
                        "full_name": formatted_name,
                        "dob": str(p_dob),
                        "gender": p_gender,
                        "phone": full_phone,
                        "address": p_address,
                        "blood_group": p_blood if p_blood != "Chưa xác định" else None,
                        "allergies": allergies_list
                    }
                    res, status_code = api_create_patient(new_patient_data)
                    if status_code in [200, 201]:
                        st.toast(f"Tạo bệnh nhân {formatted_name} thành công!", icon="✅")
                        st.success(f"Tạo bệnh nhân thành công! Mã BN: `{p_code}`")
                        st.rerun()
                    else:
                        st.error(f"Lỗi từ API: {res}")
                except Exception as e:
                    st.error(f"Lỗi kết nối API: {e}")

# --- TAB 3: CHỈNH SỬA ---
with tab_edit:
    st.subheader("Chỉnh Sửa Thông Tin Bệnh Nhân")
    search_edit = st.text_input("🔍 Tìm kiếm bệnh nhân cần sửa (Họ tên, Mã BN, SĐT):", key="search_edit_tab")
    patients_edit, _ = api_get_patients(skip=0, limit=1000, search=search_edit if search_edit else None)
    
    if patients_edit:
        patient_options_edit = {
            f"{p.get('patient_code')} - {p.get('full_name')} ({p.get('phone', 'Không có SĐT')})": str(p.get("_id") or p.get("id")) 
            for p in patients_edit
        }
        selected_label_edit = st.selectbox("Chọn bệnh nhân từ kết quả tìm kiếm:", options=list(patient_options_edit.keys()), key="select_edit_tab")
        chosen_id_edit = patient_options_edit[selected_label_edit] if selected_label_edit else None
        
        editing_p = next((p for p in patients_edit if str(p.get("_id") or p.get("id")) == chosen_id_edit), None)
        if editing_p:
            old_phone = editing_p.get("phone", "")
            if old_phone.startswith("+84"):
                old_phone_suffix = old_phone[3:]
            elif old_phone.startswith("0"):
                old_phone_suffix = old_phone[1:]
            else:
                old_phone_suffix = old_phone

            with st.form("form_edit_patient_tab"):
                ec1, ec2 = st.columns(2)
                with ec1:
                    e_code = st.text_input("Mã bệnh nhân *", value=editing_p.get("patient_code", ""))
                    raw_e_name = st.text_input("Họ và tên *", value=editing_p.get("full_name", ""))
                    
                    try:
                        default_dob = pd.to_datetime(editing_p.get("dob")).date()
                    except:
                        default_dob = pd.to_datetime("2000-01-01").date()
                    e_dob = st.date_input("Ngày sinh", value=default_dob)
                    
                    gender_options = ["Nam", "Nữ", "Khác"]
                    g_idx = gender_options.index(editing_p.get("gender")) if editing_p.get("gender") in gender_options else 0
                    e_gender = st.selectbox("Giới tính *", gender_options, index=g_idx)
                with ec2:
                    col_e_code, col_e_num = st.columns([1, 3])
                    with col_e_code:
                        st.text_input("Mã quốc gia", value="+84", disabled=True, key="prefix_edit")
                    with col_e_num:
                        e_phone_suffix = st.text_input("Số điện thoại (không cần nhập số 0 ở đầu) *", value=old_phone_suffix, max_chars=10)
                    
                    blood_options = ["Chưa xác định", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
                    b_val = editing_p.get("blood_group") if editing_p.get("blood_group") in blood_options else "Chưa xác định"
                    b_idx = blood_options.index(b_val)
                    e_blood = st.selectbox("Nhóm máu", blood_options, index=b_idx)
                    
                    allergies_str = ", ".join(editing_p.get("allergies", [])) if editing_p.get("allergies") else ""
                    e_allergies = st.text_input("Dị ứng (cách nhau bởi dấu phẩy)", value=allergies_str)
                    e_address = st.text_input("Địa chỉ thường trú", value=editing_p.get("address", ""))
                    
                submitted_update = st.form_submit_button("💾 Lưu Thay Đổi")
                if submitted_update:
                    cleaned_e_name = raw_e_name.strip()
                    e_phone_body = e_phone_suffix.strip()
                    if e_phone_body.startswith("0"):
                        e_phone_body = e_phone_body[1:]

                    vietnamese_name_regex = r"^[a-zA-ZàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵĐđ\s]+$"

                    if not e_code or not cleaned_e_name:
                        st.error("Vui lòng điền đầy đủ Mã bệnh nhân và Họ tên.")
                    elif not re.match(vietnamese_name_regex, cleaned_e_name):
                        st.error("❌ Họ và tên chỉ được chứa chữ cái!")
                    elif not e_phone_body.isdigit() or not (9 <= len(e_phone_body) <= 10):
                        st.error("❌ Số điện thoại không hợp lệ!")
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
                            "allergies": allergies_list
                        }
                        try:
                            res, status_code = api_update_patient(chosen_id_edit, update_data)
                            if status_code == 200:
                                st.toast("Cập nhật thông tin bệnh nhân thành công!", icon="✅")
                                st.success("Cập nhật thông tin bệnh nhân thành công!")
                                st.rerun()
                            else:
                                st.error(f"Lỗi từ API: {res}")
                        except Exception as e:
                            st.error(f"Lỗi kết nối API: {e}")
    else:
        st.warning("Không tìm thấy bệnh nhân phù hợp để chỉnh sửa.")

# --- TAB 4: XÓA ---
with tab_delete:
    st.subheader("Xóa Hồ Sơ Bệnh Nhân & Toàn Bộ Bệnh Án Liên Quan")
    search_del = st.text_input("🔍 Tìm kiếm bệnh nhân cần xóa (Họ tên, Mã BN, SĐT):", key="search_del_tab")
    patients_del, _ = api_get_patients(skip=0, limit=1000, search=search_del if search_del else None)
    
    if patients_del:
        patient_options_del = {
            f"{p.get('patient_code')} - {p.get('full_name')} ({p.get('phone', 'Không có SĐT')})": str(p.get("_id") or p.get("id")) 
            for p in patients_del
        }
        selected_label_del = st.selectbox("Chọn bệnh nhân từ kết quả tìm kiếm:", options=list(patient_options_del.keys()), key="select_del_tab")
        chosen_id_del = patient_options_del[selected_label_del] if selected_label_del else None
        
        target_p = next((p for p in patients_del if str(p.get("_id") or p.get("id")) == chosen_id_del), None)
        if target_p:
            st.warning(f"⚠️ Cảnh báo: Thao tác này sẽ xóa vĩnh viễn bệnh nhân **{target_p.get('full_name')}** ({target_p.get('patient_code')}) **ĐỒNG THỜI XÓA TOÀN BỘ HỒ SƠ BỆNH ÁN** liên quan!")
            
            if st.button("🗑️ Xác Nhận Xóa Bệnh Nhân & Toàn Bộ Bệnh Án", type="primary"):
                try:
                    all_records, _ = api_get_records(skip=0, limit=10000)
                    deleted_records_count = 0
                    for rec in all_records:
                        if str(rec.get("patient_id")) == str(chosen_id_del):
                            rec_id = str(rec.get("_id") or rec.get("id"))
                            api_delete_record(rec_id)
                            deleted_records_count += 1
                    
                    status_code = api_delete_patient(chosen_id_del)
                    if status_code in [200, 204]:
                        st.toast("Đã xóa vĩnh viễn bệnh nhân và các hồ sơ bệnh án liên quan!", icon="🗑️")
                        st.success(f"Đã xóa thành công bệnh nhân và {deleted_records_count} hồ sơ bệnh án liên quan!")
                        st.rerun()
                    else:
                        st.error(f"Lỗi khi xóa bệnh nhân qua API, mã lỗi: {status_code}")
                except Exception as e:
                    st.error(f"Lỗi kết nối API khi thực hiện xóa: {e}")
    else:
        st.warning("Không tìm thấy bệnh nhân phù hợp để xóa.")