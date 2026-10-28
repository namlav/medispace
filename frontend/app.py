import sys
from pathlib import Path
from datetime import datetime
import streamlit as st

# =====================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN & GIAO DIỆN HỆ THỐNG
# =====================================================================
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from frontend.api_client import api_get_patients, api_get_records
from frontend.ui_utils import (
    load_css,
    format_number,
    get_icon,
    render_sidebar_branding,
    render_workstation_header,
    render_kpi_card,
    render_workstation_footer,
)

st.set_page_config(
    page_title="MediSpace | Clinical Command Center",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Nạp hệ thống CSS Oceanic Workstation
load_css()

# Hiển thị nhận diện thương hiệu trên Sidebar
render_sidebar_branding()

# =====================================================================
# 2. TRUY VẤN DỮ LIỆU TỔNG QUAN TỪ BACKEND
# =====================================================================
connected = False
total_patients = None
total_records = None
connection_error = ""

try:
    _, total_patients = api_get_patients(skip=0, limit=1)
    _, total_records = api_get_records(skip=0, limit=1)
    connected = True
except Exception as e:
    connected = False
    connection_error = str(e)

# =====================================================================
# 3. HEADER WORKSTATION (OCEANIC CLINICAL COMMAND BAR)
# =====================================================================
status_label = "DATABASE CONNECTED" if connected else "DISCONNECTED"
status_kind = "live" if connected else "offline"

render_workstation_header(
    title="MediSpace Clinical Command Center",
    subtitle="Trạm điều hành quản lý hồ sơ bệnh án điện tử và điều phối phòng khám đa khoa trên nền tảng MongoDB NoSQL",
    badge_label=status_label,
    badge_status=status_kind,
    icon_name="hospital",
)

# =====================================================================
# 4. CHỈ SỐ KPI LÂM SÀNG TỔNG THỂ (4 CỘT)
# =====================================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    render_kpi_card(
        label="Tổng Bệnh Nhân",
        value=format_number(total_patients),
        foot="Hồ sơ định danh đang quản lý",
        icon_name="patient",
        accent_color="#0284C7",
    )

with col2:
    render_kpi_card(
        label="Tổng Bệnh Án",
        value=format_number(total_records),
        foot="Lượt khám lâm sàng đã lưu",
        icon_name="record",
        accent_color="#0369A1",
    )

with col3:
    render_kpi_card(
        label="Chuyên Khoa",
        value="03",
        foot="Tim Mạch · Da Liễu · RHM",
        icon_name="heart",
        accent_color="#075985",
    )

with col4:
    render_kpi_card(
        label="Tối Ưu Compound Index",
        value="11 ms",
        foot="IXSCAN: { department: 1, visit_date: -1 }",
        icon_name="zap",
        accent_color="#0284C7",
    )

st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

# Thanh điều khiển đồng bộ
col_sync, col_status = st.columns([1, 3], vertical_alignment="center")

with col_sync:
    # Sửa lỗi: dùng type="primary" thay vì kind="primary"
    if st.button("Làm mới dữ liệu", use_container_width=True, type="primary"):
        st.rerun()

with col_status:
    if connected:
        st.success(
            f"Hệ thống trực tuyến. Đồng bộ thành công {format_number(total_patients)} bệnh nhân và {format_number(total_records)} bệnh án từ MongoDB Atlas.",
            icon="✅",
        )
    else:
        st.error(
            "Mất kết nối tới máy chủ FastAPI Backend hoặc cơ sở dữ liệu MongoDB Atlas. Hãy kiểm tra dịch vụ backend.",
            icon="⚠️",
        )
        with st.expander("Chi tiết thông báo lỗi kỹ thuật"):
            st.code(connection_error, language="text")

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# =====================================================================
# 5. MA TRẬN ĐIỀU PHỐI TÁC VỤ LÂM SÀNG (3 MODULES)
# =====================================================================
st.subheader("Phân Hệ Chức Năng Lâm Sàng")

m1, m2, m3 = st.columns(3, gap="medium")

with m1:
    st.markdown(
        f"""
        <div class="ms-module-card">
            <div>
                <div class="ms-module-icon-box">{get_icon("patient", size=26, color="#0284C7")}</div>
                <h3 class="ms-module-title">Tiếp Đón & Quản Lý Bệnh Nhân</h3>
                <p class="ms-module-desc">
                    Tra cứu hồ sơ định danh theo mã số bệnh nhân (BN-XXXX), họ tên hoặc số điện thoại.
                    Đăng ký tiếp nhận bệnh nhân mới, quản lý thông tin hành chính và theo dõi tiền sử dị ứng thuốc.
                </p>
                <div class="ms-module-tags">
                    <span class="ms-module-tag">Mã BN-XXXX</span>
                    <span class="ms-module-tag">Tìm kiếm nhanh</span>
                    <span class="ms-module-tag">Tiền sử dị ứng</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link(
        "pages/Benh_Nhan.py",
        label="Mở Phân Hệ Bệnh Nhân",
        icon="👤",
        use_container_width=True,
    )

with m2:
    st.markdown(
        f"""
        <div class="ms-module-card">
            <div>
                <div class="ms-module-icon-box">{get_icon("record", size=26, color="#0369A1")}</div>
                <h3 class="ms-module-title">Bàn Khám Bệnh Đa Chuyên Khoa</h3>
                <p class="ms-module-desc">
                    Lập hồ sơ bệnh án động theo mô hình Polymorphic Document. Tự động chuyển đổi biểu mẫu
                    khám đặc thù cho chuyên khoa Tim Mạch, Da Liễu hoặc Răng - Hàm - Mặt kèm bảng kê đơn thuốc nhúng.
                </p>
                <div class="ms-module-tags">
                    <span class="ms-module-tag">Polymorphic Pattern</span>
                    <span class="ms-module-tag">3 Chuyên khoa</span>
                    <span class="ms-module-tag">Đơn thuốc nhúng</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link(
        "pages/Kham_Benh_Dong.py",
        label="Mở Bàn Khám Bệnh Động",
        icon="📋",
        use_container_width=True,
    )

with m3:
    st.markdown(
        f"""
        <div class="ms-module-card">
            <div>
                <div class="ms-module-icon-box">{get_icon("analytics", size=26, color="#075985")}</div>
                <h3 class="ms-module-title">Báo Cáo & Thống Kê Y Tế</h3>
                <p class="ms-module-desc">
                    Khai thác năng lực xử lý phân tích của MongoDB Aggregation Pipelines: phân bổ số ca theo
                    chuyên khoa, tháp tuổi bệnh nhân, tần suất tái khám và kiểm định hiệu năng tối ưu Compound Index.
                </p>
                <div class="ms-module-tags">
                    <span class="ms-module-tag">Aggregation Pipelines</span>
                    <span class="ms-module-tag">Tần suất tái khám</span>
                    <span class="ms-module-tag">Index Benchmark</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link(
        "pages/Thong_Ke_Y_Te.py",
        label="Mở Báo Cáo Thống Kê",
        icon="📊",
        use_container_width=True,
    )

st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

# =====================================================================
# 6. KIẾN TRÚC KỸ THUẬT & TỐI ƯU HÓA NOSQL MONGODB
# =====================================================================
st.subheader("Kiến Trúc Kỹ Thuật MongoDB Document Store")

t1, t2 = st.columns(2, gap="medium")

with t1:
    st.markdown(
        """
        <div class="ms-benchmark-box">
            <h4 style="margin: 0 0 0.5rem 0; color: var(--ms-text-title);">Mô Hình Bệnh Án Đa Hình (Polymorphic Pattern)</h4>
            <p style="font-size: 0.9rem; color: var(--ms-text-body); margin-bottom: 0.75rem;">
                Lưu trữ các bệnh án có thuộc tính lâm sàng hoàn toàn khác nhau vào chung một collection <code>medical_records</code> mà không cần bảng phụ hoặc cột NULL:
            </p>
            <ul style="font-size: 0.85rem; color: var(--ms-text-body); padding-left: 1.2rem; margin: 0; line-height: 1.8;">
                <li><strong>Tim Mạch</strong>: Huyết áp, nhịp tim, chỉ số EF, kết quả ECG và phân tầng nguy cơ.</li>
                <li><strong>Da Liễu</strong>: Vị trí tổn thương, hình thái sẩn/dát, thang điểm ngứa VAS và tiền sử tiếp xúc.</li>
                <li><strong>Răng - Hàm - Mặt</strong>: Sơ đồ nha khoa DMFT, phân loại bệnh lý răng và phương án điều trị.</li>
                <li><strong>Đơn thuốc nhúng (Embedded Prescriptions Array)</strong>: Đọc trọn gói lịch sử dùng thuốc trong 1 single-read query.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

with t2:
    st.markdown(
        """
        <div class="ms-benchmark-box">
            <h4 style="margin: 0 0 0.5rem 0; color: var(--ms-text-title);">Tối Ưu Hóa Truy Vấn & Compound Index</h4>
            <p style="font-size: 0.9rem; color: var(--ms-text-body); margin-bottom: 0.75rem;">
                Hiệu quả vượt trội được chứng minh qua <code>explain("executionStats")</code> trên 18.186 hồ sơ bệnh án:
            </p>
            <div class="ms-benchmark-grid">
                <div class="ms-benchmark-card ms-benchmark-unindexed">
                    <span class="ms-badge ms-badge-amber">TRƯỚC KHI TẠO INDEX</span>
                    <div class="ms-benchmark-stat" style="color: #92400E;">27 ms</div>
                    <div class="ms-benchmark-sub">Quét toàn bộ collection (COLLSCAN) · 18.186 tài liệu</div>
                </div>
                <div class="ms-benchmark-card ms-benchmark-indexed">
                    <span class="ms-badge ms-badge-live">COMPOUND INDEX IXSCAN</span>
                    <div class="ms-benchmark-stat" style="color: #065F46;">11 ms</div>
                    <div class="ms-benchmark-sub">Chỉ quét 6.038 khóa index · Tiết kiệm 59.3% thời gian</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =====================================================================
# 7. FOOTER
# =====================================================================
render_workstation_footer()
