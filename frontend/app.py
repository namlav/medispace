import streamlit as st
import sys
from pathlib import Path

# Thêm root dir vào sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from backend.app.core.database import get_db, get_patients_collection, get_records_collection
from backend.app.core.config import settings

st.set_page_config(
    page_title="MediSpace - Quản lý Bệnh Án NoSQL",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header
st.title("🏥 MediSpace: Hệ Thống Quản Lý Hồ Sơ Bệnh Án Điện Tử")
st.caption("Đồ án môn học: Cơ sở dữ liệu NoSQL (MongoDB) | Bệnh án đa chuyên khoa Schema-less")

# Kiểm tra trạng thái Database
col_status1, col_status2, col_status3 = st.columns(3)
try:
    db = get_db()
    db.command("ping")
    status_text = "🟢 Đã kết nối MongoDB"
    patients_count = get_patients_collection().count_documents({})
    records_count = get_records_collection().count_documents({})
except Exception as e:
    status_text = f"🔴 Chưa kết nối MongoDB ({e})"
    patients_count = 0
    records_count = 0

with col_status1:
    st.metric(label="Trạng thái CSDL", value="MongoDB", delta=status_text)
with col_status2:
    st.metric(label="Tổng số Bệnh nhân", value=f"{patients_count:,} hồ sơ")
with col_status3:
    st.metric(label="Tổng lượt Khám bệnh", value=f"{records_count:,} bệnh án")

st.markdown("---")

# Giới thiệu phân công công việc
st.subheader("👥 Phân Công Trách Nhiệm Nhóm 3 Sinh Viên")
col_sv1, col_sv2, col_sv3 = st.columns(3)

with col_sv1:
    st.info("""
    **SV1: Data Architect & CRUD Lead**
    * Thiết kế cấu trúc Document bệnh án đa chuyên khoa.
    * Xây dựng Core Models và API CRUD Bệnh nhân & Phiếu khám.
    * Thao tác tạo bệnh án mẫu đa chuyên khoa trong demo.
    """)

with col_sv2:
    st.success("""
    **SV2: Advanced Query Specialist**
    * Xây dựng Aggregation Pipelines thống kê dịch tễ.
    * Phân tích phân bố độ tuổi và tần suất tái khám.
    * Tối ưu hóa chỉ mục (Indexes) và đo đạc `executionStats`.
    """)

with col_sv3:
    st.warning("""
    **SV3: Fullstack Integrator & DB Tester**
    * Nạp bộ dữ liệu mẫu (>= 100 BN, >= 100 lượt khám).
    * Thiết kế giao diện Form nhập bệnh án động (Dynamic Form).
    * Thực hiện Backup/Restore và điều phối kịch bản bảo vệ.
    """)

st.markdown("---")
st.subheader("🎯 Hướng dẫn sử dụng nhanh")
st.markdown("""
1. **Quản lý Bệnh nhân (Trang 1)**: Xem danh sách, tìm kiếm và tạo mới hồ sơ bệnh nhân.
2. **Khám bệnh động (Trang 2)**: Chọn chuyên khoa (Tim Mạch, Da Liễu, Răng - Hàm - Mặt), form nhập liệu sẽ tự động thay đổi theo đặc thù từng khoa, chứng minh tính linh hoạt của MongoDB Schema-less.
3. **Thống kê y tế (Trang 3)**: Kích hoạt các báo cáo dịch tễ, biểu đồ phân tích và xem câu lệnh MongoDB Aggregation Pipeline thực thi.
""")
