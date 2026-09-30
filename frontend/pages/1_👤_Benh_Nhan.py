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

tab_list, tab_create = st.tabs(["📋 Danh Sách Bệnh Nhân", "➕ Thêm Bệnh Nhân Mới"])

with tab_list:
    search_query = st.text_input("🔍 Tìm kiếm theo Họ tên, Mã bệnh nhân hoặc Số điện thoại:", "")
    patients, total = PatientService.list_patients(skip=0, limit=100, search=search_query if search_query else None)
    
    st.write(f"Tìm thấy **{total}** hồ sơ bệnh nhân (hiển thị tối đa 100):")
    
    if patients:
        table_data = []
        for p in patients:
            table_data.append({
                "Mã BN": p.get("patient_code"),
                "Họ và Tên": p.get("full_name"),
                "Ngày sinh": p.get("dob"),
                "Giới tính": p.get("gender"),
                "Điện thoại": p.get("phone"),
                "Nhóm máu": p.get("blood_group"),
                "Dị ứng": ", ".join(p.get("allergies", [])) if p.get("allergies") else "Không",
                "Địa chỉ": p.get("address")
            })
        st.dataframe(pd.DataFrame(table_data), use_container_width=True)
    else:
        st.warning("Chưa có hồ sơ bệnh nhân nào. Vui lòng nạp dữ liệu bằng script 'scripts/seed_data.py' hoặc thêm mới ở tab bên cạnh.")

with tab_create:
    st.subheader("Tạo Hồ Sơ Bệnh Nhân Mới")
    with st.form("form_create_patient"):
        c1, c2 = st.columns(2)
        with c1:
            p_code = st.text_input("Mã bệnh nhân *", value=f"BN-{total + 1:04d}")
            p_name = st.text_input("Họ và tên *", placeholder="Ví dụ: Nguyễn Văn An")
            p_dob = st.date_input("Ngày sinh")
            p_gender = st.selectbox("Giới tính *", ["Nam", "Nữ", "Khác"])
        with c2:
            p_phone = st.text_input("Số điện thoại", placeholder="Ví dụ: 0912345678")
            p_blood = st.selectbox("Nhóm máu", ["Chưa xác định", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
            p_allergies = st.text_input("Dị ứng (cách nhau bởi dấu phẩy)", placeholder="Ví dụ: Penicillin, Hải sản")
            p_address = st.text_input("Địa chỉ thường trú", placeholder="Số nhà, đường, quận/huyện, tỉnh/TP")
            
        submitted = st.form_submit_button("💾 Lưu Hồ Sơ Bệnh Nhân", use_container_width=True)
        if submitted:
            if not p_code or not p_name:
                st.error("Vui lòng điền đầy đủ Mã bệnh nhân và Họ tên.")
            else:
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
                try:
                    res = PatientService.create_patient(new_patient)
                    st.success(f"Tạo bệnh nhân thành công! ID MongoDB: `{res.get('id')}`")
                    st.json(res)
                except Exception as e:
                    st.error(f"Lỗi khi lưu bệnh nhân: {e}")
