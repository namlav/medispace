import streamlit as st
import sys
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

from backend.app.services.patient_service import PatientService
from backend.app.models.patient import PatientCreate

st.set_page_config(page_title="Quản Lý Bệnh Nhân | MediSpace", page_icon="👤", layout="wide")

st.title("👤 Quản Lý Hồ Sơ Bệnh Nhân")
st.caption("Quản lý thông tin hành chính bệnh nhân trong collection 'patients'")

# Tạo 4 Tab chính trên cùng một hàng
tab_list, tab_create, tab_edit, tab_delete = st.tabs([
    "📋 Danh Sách Bệnh Nhân", 
    "➕ Thêm Bệnh Nhân Mới", 
    "✏️ Chỉnh Sửa Bệnh Nhân", 
    "🗑️ Xóa Bệnh Nhân"
])

# Lấy tổng số lượng để gợi ý mã bệnh nhân mới
_, total_all = PatientService.list_patients(skip=0, limit=1000)

# --- TAB 1: DANH SÁCH ---
with tab_list:
    c_search, c_limit = st.columns([3, 1])
    with c_search:
        search_query = st.text_input("🔍 Tìm kiếm theo Họ tên, Mã bệnh nhân hoặc Số điện thoại:", key="search_tab_1")
    with c_limit:
        limit_val = st.selectbox("Hiển thị tối đa:", [100, 200, 500, "Tất cả"], index=1)
        actual_limit = 10000 if limit_val == "Tất cả" else limit_val

    patients, total = PatientService.list_patients(skip=0, limit=actual_limit, search=search_query if search_query else None)
    
    st.write(f"Hiển thị **{len(patients)}** / **{total}** hồ sơ bệnh nhân:")
    
    if patients:
        table_data = []
        for p in patients:
            table_data.append({
                "ID Hệ Thống": str(p.get("_id")),
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
            width='stretch',
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
            p_name = st.text_input("Họ và tên *", placeholder="Ví dụ: Nguyễn Văn An")
            p_dob = st.date_input("Ngày sinh")
            p_gender = st.selectbox("Giới tính *", ["Nam", "Nữ", "Khác"])
        with c2:
            p_phone = st.text_input("Số điện thoại", placeholder="Ví dụ: 0912345678")
            p_blood = st.selectbox("Nhóm máu", ["Chưa xác định", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
            p_allergies = st.text_input("Dị ứng (cách nhau bởi dấu phẩy)", placeholder="Ví dụ: Penicillin, Hải sản")
            p_address = st.text_input("Địa chỉ thường trú", placeholder="Số nhà, đường, quận/huyện, tỉnh/TP")
            
        submitted = st.form_submit_button("💾 Lưu Hồ Sơ Bệnh Nhân")
        if submitted:
            if not p_code or not p_name:
                st.error("Vui lòng điền đầy đủ Mã bệnh nhân và Họ tên.")
            else:
                try:
                    allergies_list = [a.strip() for a in p_allergies.split(",") if a.strip()] if p_allergies else []
                    new_patient = PatientCreate(
                        patient_code=p_code,
                        full_name=p_name,
                        dob=str(p_dob),
                        gender=p_gender,
                        phone=p_phone,
                        address=p_address,
                        blood_group=p_blood if p_blood != "Chưa xác định" else None,
                        allergies=allergies_list
                    )
                    res = PatientService.create_patient(new_patient)
                    st.toast(f"Tạo bệnh nhân {p_name} thành công!", icon="✅")
                    st.success(f"Tạo bệnh nhân thành công! Mã BN: `{p_code}` - ID MongoDB: `{res.get('id')}`")
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi chi tiết khi lưu bệnh nhân: {e}")

# --- TAB 3: CHỈNH SỬA ---
with tab_edit:
    st.subheader("Chỉnh Sửa Thông Tin Bệnh Nhân")
    search_edit = st.text_input("🔍 Tìm kiếm bệnh nhân cần sửa (Họ tên, Mã BN, SĐT):", key="search_edit_tab")
    patients_edit, _ = PatientService.list_patients(skip=0, limit=1000, search=search_edit if search_edit else None)
    
    if patients_edit:
        patient_options_edit = {
            f"{p.get('patient_code')} - {p.get('full_name')} ({p.get('phone', 'Không có SĐT')})": str(p.get("_id")) 
            for p in patients_edit
        }
        selected_label_edit = st.selectbox("Chọn bệnh nhân từ kết quả tìm kiếm:", options=list(patient_options_edit.keys()), key="select_edit_tab")
        chosen_id_edit = patient_options_edit[selected_label_edit] if selected_label_edit else None
        
        editing_p = next((p for p in patients_edit if str(p.get("_id")) == chosen_id_edit), None)
        if editing_p:
            with st.form("form_edit_patient_tab"):
                ec1, ec2 = st.columns(2)
                with ec1:
                    e_code = st.text_input("Mã bệnh nhân *", value=editing_p.get("patient_code", ""))
                    e_name = st.text_input("Họ và tên *", value=editing_p.get("full_name", ""))
                    try:
                        default_dob = pd.to_datetime(editing_p.get("dob")).date()
                    except:
                        default_dob = pd.to_datetime("2000-01-01").date()
                    e_dob = st.date_input("Ngày sinh", value=default_dob)
                    
                    gender_options = ["Nam", "Nữ", "Khác"]
                    g_idx = gender_options.index(editing_p.get("gender")) if editing_p.get("gender") in gender_options else 0
                    e_gender = st.selectbox("Giới tính *", gender_options, index=g_idx)
                with ec2:
                    e_phone = st.text_input("Số điện thoại", value=editing_p.get("phone", ""))
                    
                    blood_options = ["Chưa xác định", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
                    b_val = editing_p.get("blood_group") if editing_p.get("blood_group") in blood_options else "Chưa xác định"
                    b_idx = blood_options.index(b_val)
                    e_blood = st.selectbox("Nhóm máu", blood_options, index=b_idx)
                    
                    allergies_str = ", ".join(editing_p.get("allergies", [])) if editing_p.get("allergies") else ""
                    e_allergies = st.text_input("Dị ứng (cách nhau bởi dấu phẩy)", value=allergies_str)
                    e_address = st.text_input("Địa chỉ thường trú", value=editing_p.get("address", ""))
                    
                submitted_update = st.form_submit_button("💾 Lưu Thay Đổi")
                if submitted_update:
                    if not e_code or not e_name:
                        st.error("Vui lòng điền đầy đủ Mã bệnh nhân và Họ tên.")
                    else:
                        allergies_list = [a.strip() for a in e_allergies.split(",") if a.strip()] if e_allergies else []
                        update_data = {
                            "patient_code": e_code,
                            "full_name": e_name,
                            "dob": str(e_dob),
                            "gender": e_gender,
                            "phone": e_phone,
                            "address": e_address,
                            "blood_group": e_blood if e_blood != "Chưa xác định" else None,
                            "allergies": allergies_list
                        }
                        try:
                            PatientService.update_patient(chosen_id_edit, update_data)
                            st.toast("Cập nhật thông tin bệnh nhân thành công!", icon="✅")
                            st.success("Cập nhật thông tin bệnh nhân thành công!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi khi cập nhật: {e}")
    else:
        st.warning("Không tìm thấy bệnh nhân phù hợp để chỉnh sửa.")

# --- TAB 4: XÓA ---
with tab_delete:
    st.subheader("Xóa Hồ Sơ Bệnh Nhân")
    search_del = st.text_input("🔍 Tìm kiếm bệnh nhân cần xóa (Họ tên, Mã BN, SĐT):", key="search_del_tab")
    patients_del, _ = PatientService.list_patients(skip=0, limit=1000, search=search_del if search_del else None)
    
    if patients_del:
        patient_options_del = {
            f"{p.get('patient_code')} - {p.get('full_name')} ({p.get('phone', 'Không có SĐT')})": str(p.get("_id")) 
            for p in patients_del
        }
        selected_label_del = st.selectbox("Chọn bệnh nhân từ kết quả tìm kiếm:", options=list(patient_options_del.keys()), key="select_del_tab")
        chosen_id_del = patient_options_del[selected_label_del] if selected_label_del else None
        
        target_p = next((p for p in patients_del if str(p.get("_id")) == chosen_id_del), None)
        if target_p:
            st.warning(f"⚠️ Bạn có chắc chắn muốn xóa vĩnh viễn bệnh nhân **{target_p.get('full_name')}** ({target_p.get('patient_code')}) không?")
            if st.button("🗑️ Xác Nhận Xóa Vĩnh Viễn", type="primary"):
                try:
                    PatientService.delete_patient(chosen_id_del)
                    st.toast("Đã xóa hồ sơ bệnh nhân thành công!", icon="🗑️")
                    st.success("Đã xóa hồ sơ bệnh nhân thành công!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi khi xóa: {e}")
    else:
        st.warning("Không tìm thấy bệnh nhân phù hợp để xóa.")