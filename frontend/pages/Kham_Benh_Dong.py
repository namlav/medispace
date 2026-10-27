import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))
from frontend.ui_utils import load_css

from frontend.api_client import (
    api_get_patients,
    api_get_records,
    api_create_record,
    api_update_record,
    api_delete_record,
)

DEPARTMENTS = ["TIM_MACH", "DA_LIEU", "RANG_HAM_MAT"]

st.set_page_config(
    page_title="Quản Lý Hồ Sơ Bệnh Án Động | MediSpace", page_icon="📋", layout="wide"
)
load_css("medical_form.css")

# ============================================================
# MEDISPACE - MEDICAL RECORDS UI
# Chỉ thay đổi giao diện, giữ nguyên xử lý nghiệp vụ
# ============================================================

st.markdown(
    """
<style>
:root {
    --ms-primary: #167D70;
    --ms-primary-dark: #10665B;
    --ms-primary-soft: #E8F5F2;
    --ms-background: #F5F8FA;
    --ms-heading: #203B49;
    --ms-text: #526672;
    --ms-muted: #80909A;
    --ms-border: #E1E9ED;
}

/* Nền tổng thể */
.stApp {
    background: var(--ms-background);
}

.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

/* Header */
.ms-record-header {
    position: relative;
    background: linear-gradient(
        115deg,
        #FFFFFF 0%,
        #E8F5F2 100%
    );
    border: 1px solid #DCEBE7;
    border-radius: 18px;
    padding: 34px 38px;
    margin-bottom: 26px;
    overflow: hidden;
}

.ms-record-header::after {
    content: "";
    position: absolute;
    width: 190px;
    height: 190px;
    border-radius: 50%;
    background: rgba(22, 125, 112, 0.06);
    top: -95px;
    right: -40px;
    pointer-events: none;
}

.ms-record-eyebrow {
    font-size: 12px;
    color: var(--ms-primary);
    font-weight: 700;
    letter-spacing: 1.5px;
    margin-bottom: 13px;
}

.ms-record-title {
    font-size: clamp(28px, 3vw, 38px);
    font-weight: 750;
    line-height: 1.25;
    color: var(--ms-heading);
    margin: 0 0 12px;
}

.ms-record-description {
    font-size: 14px;
    line-height: 1.8;
    color: var(--ms-text);
    max-width: 760px;
    margin: 0;
}

/* Tab điều hướng */
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF;
    border: 1px solid var(--ms-border);
    border-radius: 13px;
    padding: 7px;
    gap: 7px;
    margin-bottom: 22px;
    flex-wrap: wrap;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 9px;
    padding: 11px 18px;
    color: var(--ms-text);
    font-weight: 600;
    font-size: 13px;
}

.stTabs [aria-selected="true"] {
    background: var(--ms-primary-soft) !important;
    color: var(--ms-primary) !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    background: transparent;
}

/* Nội dung trong mỗi tab */
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 10px;
}

/* Tiêu đề */
h2, h3 {
    color: var(--ms-heading);
    font-weight: 700;
}

.ms-record-section {
    margin: 12px 0 22px;
}

.ms-record-section-title {
    color: var(--ms-heading);
    font-size: 21px;
    font-weight: 700;
    margin-bottom: 7px;
}

.ms-record-section-description {
    color: var(--ms-muted);
    font-size: 13px;
    line-height: 1.7;
}

/* Tiêu đề nhóm thông tin */
.ms-record-group {
    background: #FFFFFF;
    border-left: 4px solid var(--ms-primary);
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    margin: 24px 0 18px;
    box-shadow: 0 2px 10px rgba(32,59,73,0.025);
}

.ms-record-group-title {
    font-size: 16px;
    font-weight: 700;
    color: var(--ms-heading);
}

.ms-record-group-note {
    font-size: 12px;
    color: var(--ms-muted);
    margin-top: 5px;
}

/* Label */
[data-testid="stWidgetLabel"] p {
    color: var(--ms-heading);
    font-size: 13px;
    font-weight: 600;
}

/* Input */
.stTextInput input,
.stNumberInput input,
.stDateInput input {
    background: #FFFFFF;
    border-radius: 9px;
    color: var(--ms-heading);
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stDateInput input:focus {
    border-color: var(--ms-primary);
}

/* Selectbox */
.stSelectbox [data-baseweb="select"] > div,
.stMultiSelect [data-baseweb="select"] > div {
    border-radius: 9px;
    background: #FFFFFF;
}

/* Checkbox */
.stCheckbox {
    padding: 5px 0;
}

/* Nút */
.stButton > button {
    border-radius: 9px;
    min-height: 42px;
    font-weight: 600;
    transition: background-color 0.2s ease;
}

.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background: var(--ms-primary);
    border-color: var(--ms-primary);
    color: #FFFFFF;
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background: var(--ms-primary-dark);
    border-color: var(--ms-primary-dark);
}

/* Thẻ cảnh báo và thông báo */
[data-testid="stAlert"] {
    border-radius: 11px;
}

/* Tra cứu: hồ sơ mở rộng */
[data-testid="stExpander"] {
    background: #FFFFFF;
    border: 1px solid var(--ms-border);
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 12px;
}

[data-testid="stExpander"] summary {
    padding: 6px 4px;
    color: var(--ms-heading);
    font-weight: 500;
}

/* Bảng đơn thuốc */
[data-testid="stDataFrame"] {
    border-radius: 11px;
    border: 1px solid var(--ms-border);
    overflow: hidden;
}

/* JSON Document */
[data-testid="stJson"] {
    border-radius: 11px;
    padding: 12px;
}

/* Đường phân cách */
hr {
    border-color: var(--ms-border);
    opacity: 0.8;
}

/* Footer */
.ms-record-footer {
    border-top: 1px solid var(--ms-border);
    margin-top: 40px;
    padding-top: 18px;
    text-align: center;
    font-size: 12px;
    color: var(--ms-muted);
}

/* Màn hình nhỏ */
@media (max-width: 768px) {
    .ms-record-header {
        padding: 24px;
    }

    .stTabs [data-baseweb="tab"] {
        font-size: 12px;
        padding: 9px 11px;
    }

    .ms-record-group {
        padding: 12px 14px;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# MEDISPACE - MEDICAL RECORDS V2
# Chỉ nâng cấp giao diện: ảnh, hiệu ứng, hover, watermark
# Không thay đổi Backend, API hoặc luồng CRUD
# ============================================================

from urllib.parse import quote

record_hero_svg = """
<svg xmlns="http://www.w3.org/2000/svg"
viewBox="0 0 520 340" fill="none">

<defs>
 <linearGradient id="paper" x1="0" y1="0" x2="1" y2="1">
  <stop stop-color="#FFFFFF"/>
  <stop offset="1" stop-color="#EAF7F3"/>
 </linearGradient>
 <filter id="shadow" x="-40%" y="-40%" width="180%" height="180%">
  <feDropShadow dx="0" dy="12" stdDeviation="12"
  flood-color="#167D70" flood-opacity=".15"/>
 </filter>
</defs>

<!-- Nền -->
<circle cx="265" cy="172" r="145" fill="#CBEAE3" opacity=".65"/>
<circle cx="430" cy="70" r="23" fill="#B3DBD2" opacity=".8"/>
<circle cx="88" cy="270" r="18" fill="#A9D8CE" opacity=".6"/>

<!-- Hồ sơ y tế -->
<rect x="133" y="37" width="240" height="270" rx="19"
 fill="url(#paper)" stroke="#C9E5DD"
 stroke-width="2" filter="url(#shadow)"/>

<path d="M133 56 Q133 37 152 37 H354 Q373 37 373 56 V97 H133 Z"
 fill="#167D70"/>

<rect x="156" y="60" width="105" height="11" rx="5"
 fill="#FFFFFF" opacity=".9"/>

<rect x="156" y="112" width="68" height="7" rx="3"
 fill="#8FCBC0"/>

<rect x="156" y="133" width="178" height="7" rx="3"
 fill="#BCDCD5"/>

<rect x="156" y="151" width="141" height="7" rx="3"
 fill="#BCDCD5"/>

<!-- Biểu đồ đường sinh hiệu -->
<rect x="155" y="177" width="195" height="68" rx="11"
 fill="#F0FAF7" stroke="#D5EAE4"/>

<path d="M170 211 H190 L200 197 L211 228 L222 184
 L235 215 H252 L263 205 L273 211 H335"
 stroke="#167D70" stroke-width="4"
 stroke-linecap="round" stroke-linejoin="round"/>

<rect x="156" y="261" width="135" height="7" rx="3"
 fill="#9DCFC5"/>
<rect x="156" y="279" width="100" height="7" rx="3"
 fill="#C0DDD6"/>

<!-- Thẻ hồ sơ bên trái -->
<rect x="49" y="126" width="108" height="111" rx="15"
 fill="#FFFFFF" stroke="#D5E9E4" filter="url(#shadow)"/>

<rect x="65" y="145" width="74" height="9" rx="4"
 fill="#167D70" opacity=".85"/>
<rect x="65" y="167" width="60" height="7" rx="3"
 fill="#ADD6CD"/>
<rect x="65" y="184" width="73" height="7" rx="3"
 fill="#ADD6CD"/>
<rect x="65" y="201" width="48" height="7" rx="3"
 fill="#ADD6CD"/>

<!-- Thẻ đơn thuốc bên phải -->
<rect x="352" y="198" width="116" height="91" rx="14"
 fill="#FFFFFF" stroke="#D5E9E4" filter="url(#shadow)"/>

<rect x="368" y="214" width="82" height="8" rx="4"
 fill="#167D70" opacity=".8"/>
<rect x="368" y="235" width="67" height="7" rx="3"
 fill="#ADD6CD"/>
<rect x="368" y="253" width="78" height="7" rx="3"
 fill="#ADD6CD"/>

</svg>
"""

# SVG được mã hóa thành CSS URL để tránh lỗi HTML Base64.
record_hero_url = "data:image/svg+xml," + quote(record_hero_svg, safe="")

record_v2_css = """
<style>

/* ===========================================
   1. HERO - HỒ SƠ BỆNH ÁN ĐIỆN TỬ
   =========================================== */

.ms-record-header {
    position: relative;
    isolation: isolate;
    overflow: hidden;

    min-height: 275px;
    padding: 38px 40% 38px 38px;

    background: linear-gradient(
        115deg,
        #FFFFFF 0%,
        #E8F5F2 53%,
        #D8EEE8 100%
    );

    background-size: 200% 200%;
    animation: recordGradient 15s ease-in-out infinite;
}

/* Ảnh minh họa */
.ms-record-header::after {
    content: "";
    position: absolute;

    width: 39%;
    height: 275px;
    max-width: 450px;

    right: 4px;
    top: 50%;
    z-index: 1;

    background-image: url("__RECORD_HERO_IMAGE__");
    background-size: contain;
    background-position: center;
    background-repeat: no-repeat;

    transform: translateY(-50%);
    animation: recordFloat 6s ease-in-out infinite;

    pointer-events: none;
}

/* Vòng sáng nền */
.ms-record-header::before {
    content: "";
    position: absolute;
    z-index: 0;

    width: 270px;
    height: 270px;

    right: 6%;
    bottom: -140px;

    border-radius: 50%;
    background: radial-gradient(
        circle,
        rgba(85,185,174,.24),
        transparent
    );

    animation: recordGlow 9s ease-in-out infinite;
    pointer-events: none;
}

/* Nội dung của Header */
.ms-record-header > * {
    position: relative;
    z-index: 2;
}

.ms-record-title {
    letter-spacing: -.5px;
}

.ms-record-description {
    max-width: 680px;
    line-height: 1.85;
}


/* ===========================================
   2. BỐN TAB CRUD
   =========================================== */

.stTabs [data-baseweb="tab-list"] {
    border-radius: 14px;
    box-shadow: 0 4px 16px rgba(32,59,73,.035);
}

.stTabs [data-baseweb="tab"] {
    transition:
        color .25s ease,
        background-color .25s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    background: #F0F8F6;
    color: #167D70;
}

.stTabs [aria-selected="true"] {
    background: #E8F5F2 !important;
    color: #167D70 !important;
}


/* ===========================================
   3. NHÓM BIỂU MẪU CHUYÊN KHOA
   =========================================== */

.ms-record-group {
    position: relative;
    overflow: hidden;

    border-left: 4px solid #167D70;
    background: linear-gradient(
        110deg,
        #FFFFFF,
        #F0F9F6
    );

    border-radius: 0 12px 12px 0;

    transition:
        transform .3s ease,
        box-shadow .3s ease,
        border-color .3s ease;
}

.ms-record-group::after {
    content: "";
    position: absolute;

    width: 115px;
    height: 115px;

    right: -25px;
    top: -42px;

    background: rgba(22,125,112,.055);
    border-radius: 50%;
    pointer-events: none;
}

.ms-record-group:hover {
    transform: translateY(-3px);
    border-left-color: #55B9AE;
    box-shadow: 0 9px 23px rgba(22,125,112,.08);
}


/* ===========================================
   4. INPUT VÀ BỘ CHỌN
   =========================================== */

.stTextInput input,
.stNumberInput input,
.stDateInput input {
    transition:
        border-color .25s ease,
        box-shadow .25s ease;
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stDateInput input:focus {
    border-color: #167D70;
    box-shadow: 0 0 0 1px rgba(22,125,112,.16);
}


/* ===========================================
   5. NÚT LƯU, SỬA, XÓA
   =========================================== */

.stButton > button {
    transition:
        transform .25s ease,
        box-shadow .25s ease,
        background-color .25s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 7px 18px rgba(22,125,112,.12);
}


/* ===========================================
   6. THẺ TRA CỨU BỆNH ÁN
   =========================================== */

[data-testid="stExpander"] {
    border: 1px solid #E1E9ED;
    background: linear-gradient(
        120deg,
        #FFFFFF,
        #FCFEFD
    );

    border-radius: 13px;
    box-shadow: 0 3px 14px rgba(32,59,73,.025);

    transition:
        transform .28s ease,
        box-shadow .28s ease,
        border-color .28s ease;
}

[data-testid="stExpander"]:hover {
    border-color: #B7DED5;
    box-shadow: 0 9px 22px rgba(22,125,112,.07);
}


/* ===========================================
   7. BẢNG ĐƠN THUỐC
   =========================================== */

[data-testid="stDataFrame"] {
    border-radius: 13px;
    border: 1px solid #E1E9ED;

    transition:
        border-color .25s ease,
        box-shadow .25s ease;
}

[data-testid="stDataFrame"]:hover {
    border-color: #B7DED5;
    box-shadow: 0 8px 22px rgba(22,125,112,.06);
}


/* ===========================================
   8. KHUNG DỮ LIỆU JSON
   =========================================== */

[data-testid="stJson"] {
    border: 1px solid #E1E9ED;
    border-radius: 12px;
    background: #F8FBFA;
}


/* ===========================================
   9. HIỆU ỨNG CHUYỂN ĐỘNG
   =========================================== */

@keyframes recordGradient {
    0%, 100% {
        background-position: 0% 50%;
    }

    50% {
        background-position: 100% 50%;
    }
}

@keyframes recordFloat {
    0%, 100% {
        transform: translateY(-50%);
    }

    50% {
        transform: translateY(calc(-50% - 8px));
    }
}

@keyframes recordGlow {
    0%, 100% {
        opacity: .4;
        transform: scale(1);
    }

    50% {
        opacity: .8;
        transform: scale(1.12);
    }
}


/* ===========================================
   10. RESPONSIVE
   =========================================== */

@media (max-width: 1000px) {
    .ms-record-header {
        padding-right: 36%;
    }

    .ms-record-header::after {
        width: 34%;
    }
}

@media (max-width: 760px) {
    .ms-record-header {
        min-height: 0;
        padding: 26px 23px;
    }

    .ms-record-header::after {
        display: none;
    }
}

/* Hạn chế chuyển động khi người dùng yêu cầu */
@media (prefers-reduced-motion: reduce) {
    .ms-record-header,
    .ms-record-header::before,
    .ms-record-header::after {
        animation: none !important;
    }

    .ms-record-group,
    .stButton > button,
    [data-testid="stExpander"],
    [data-testid="stDataFrame"] {
        transition: none !important;
    }
}

</style>
"""

st.markdown(
    """
<style>
.ms-record-group::before {
    content: "HS";
    position: absolute;
    right: 28px;
    bottom: 5px;
    font-size: 44px;
    font-weight: 800;
    color: rgba(22,125,112,.055);
    pointer-events: none;
}
</style>
""",
    unsafe_allow_html=True,
)

record_v2_css = record_v2_css.replace("__RECORD_HERO_IMAGE__", record_hero_url)

st.markdown(record_v2_css, unsafe_allow_html=True)


def record_html(html):
    cleaned = "\n".join(line.lstrip() for line in html.splitlines()).strip()

    st.markdown(cleaned, unsafe_allow_html=True)


def record_section(title, description=""):
    record_html(f"""
    <div class="ms-record-section">
        <div class="ms-record-section-title">
            {title}
        </div>
        <div class="ms-record-section-description">
            {description}
        </div>
    </div>
    """)


def record_group(title, description=""):
    record_html(f"""
    <div class="ms-record-group">
        <div class="ms-record-group-title">
            {title}
        </div>
        <div class="ms-record-group-note">
            {description}
        </div>
    </div>
    """)


# ============================================================
# HEADER - QUẢN LÝ HỒ SƠ BỆNH ÁN
# ============================================================

record_html("""
<div class="ms-record-header">
    <div class="ms-record-eyebrow">
        MEDISPACE · MEDICAL RECORDS MANAGEMENT
    </div>

    <h1 class="ms-record-title">
        Quản lý hồ sơ bệnh án
    </h1>

    <p class="ms-record-description">
        Quản lý hồ sơ khám bệnh điện tử,
        tra cứu lịch sử điều trị và cập nhật bệnh án
        theo từng chuyên khoa trên nền tảng MongoDB.
    </p>
</div>
""")

# Giữ nguyên 4 tab và thứ tự chức năng
tab_create, tab_search, tab_edit, tab_delete = st.tabs(
    ["Khám bệnh & Lập hồ sơ mới", "Tra cứu bệnh án", "Chỉnh sửa bệnh án", "Xóa bệnh án"]
)


# Tải danh sách bệnh nhân qua API
try:
    all_patients, _ = api_get_patients(skip=0, limit=1000)
except Exception:
    st.error(
        "Không kết nối được FastAPI Backend. Hãy kiểm tra backend đang chạy ở cổng 8000."
    )
    st.stop()
patient_map = {str(p.get("_id") or p.get("id")): p for p in all_patients}

# ==========================================
# TAB 1: KHÁM BỆNH & LẬP HỒ SƠ BỆNH ÁN MỚI
# ==========================================
with tab_create:
    if not all_patients:
        st.warning(
            "Chưa có bệnh nhân nào trong hệ thống! Vui lòng tạo bệnh nhân trước."
        )
        st.stop()

    patient_options = {
        f"{p.get('patient_code')} - {p.get('full_name')} ({p.get('gender')}, {p.get('dob')})": str(
            p.get("_id") or p.get("id")
        )
        for p in all_patients
    }

    selected_patient_label = st.selectbox(
        "1. Chọn Bệnh Nhân Thăm Khám:",
        list(patient_options.keys()),
        key="select_patient_create",
    )
    selected_patient_id = patient_options[selected_patient_label]

    col_main1, col_main2 = st.columns(2)
    with col_main1:
        selected_dept = st.selectbox(
            "2. Chọn Chuyên Khoa Khám:",
            options=DEPARTMENTS,
            format_func=lambda x: {
                "TIM_MACH": "Khoa Tim Mạch",
                "DA_LIEU": "Khoa Da Liễu",
                "RANG_HAM_MAT": "🦷 Khoa Răng - Hàm - Mặt",
            }.get(x, x),
            key="select_dept_create",
        )
        doctor_name = st.text_input(
            "Bác sĩ phụ trách:",
            value=(
                "BS. CKII Nguyễn Văn Hùng"
                if selected_dept == "TIM_MACH"
                else (
                    "BS. CKI Trần Thị B"
                    if selected_dept == "DA_LIEU"
                    else "BS. CKI Lê Hoàng C"
                )
            ),
            key="doc_name_create",
        )

    with col_main2:
        now_utc = datetime.now(timezone.utc)
        record_code = st.text_input(
            "Mã phiếu khám:",
            value=f"BA-{now_utc.strftime('%Y%m%d')}-{now_utc.strftime('%H%M%S')}",
            key="rec_code_create",
        )
        symptoms = st.text_input(
            "Lý do khám / Triệu chứng lâm sàng:",
            placeholder="Ví dụ: Đau tức ngực, hồi hộp...",
            key="symp_create",
        )
        diagnosis = st.text_input(
            "Chẩn đoán bệnh:",
            placeholder="Ví dụ: Tăng huyết áp độ 2...",
            key="diag_create",
        )

        st.markdown("---")

    dept_names = {
        "TIM_MACH": "Tim mạch",
        "DA_LIEU": "Da liễu",
        "RANG_HAM_MAT": "Răng - Hàm - Mặt",
    }

    record_group(
        f"Dữ liệu khám chuyên khoa {dept_names.get(selected_dept, selected_dept)}",
        "Các trường thông tin thay đổi theo chuyên khoa khám.",
    )

    specialty_data = {}
    if selected_dept == "TIM_MACH":
        c1, c2, c3 = st.columns(3)
        with c1:
            systolic = st.number_input(
                "Huyết áp tâm thu (mmHg):",
                min_value=60,
                max_value=250,
                value=140,
                key="c_sys",
            )
            diastolic = st.number_input(
                "Huyết áp tâm trương (mmHg):",
                min_value=40,
                max_value=150,
                value=90,
                key="c_dia",
            )
        with c2:
            heart_rate = st.number_input(
                "Nhịp tim (lần/phút):",
                min_value=40,
                max_value=200,
                value=82,
                key="c_hr",
            )
            ef = st.number_input(
                "Chỉ số phân suất tống máu EF (%):",
                min_value=20,
                max_value=85,
                value=58,
                key="c_ef",
            )
        with c3:
            ecg = st.selectbox(
                "Kết quả Điện tâm đồ (ECG):",
                [
                    "Nhịp xoang bình thường",
                    "Nhịp xoang nhanh, ST chênh xuống nhẹ",
                    "Ngoại tâm thu thất rải rác",
                    "Phì đại thất trái",
                ],
                key="c_ecg",
            )
            risk = st.selectbox(
                "Phân tầng nguy cơ tim mạch:",
                ["Thấp", "Trung bình", "Cao", "Rất cao"],
                key="c_risk",
            )

        specialty_data = {
            "blood_pressure": {"systolic": systolic, "diastolic": diastolic},
            "heart_rate_bpm": heart_rate,
            "ejection_fraction_ef": ef,
            "ecg_result": ecg,
            "cardiovascular_risk": risk,
        }
    elif selected_dept == "DA_LIEU":
        c1, c2 = st.columns(2)
        with c1:
            locations = st.multiselect(
                "Vị trí tổn thương da:",
                [
                    "Khuôn mặt",
                    "Cẳng tay",
                    "Bàn tay",
                    "Lưng",
                    "Vùng ngực",
                    "Da đầu",
                    "Cẳng chân",
                ],
                default=["Cẳng tay"],
                key="d_loc",
            )
            lesion_type = st.selectbox(
                "Loại thương tổn đặc trưng:",
                [
                    "Mảng hồng ban giới hạn rõ",
                    "Sẩn viêm, mụn mủ hoại tử",
                    "Mụn nước mọc thành chùm rải rác",
                    "Vảy nến bong tróc màu bạc",
                    "Mảng thâm sạm tăng sắc tố",
                ],
                key="d_type",
            )
        with c2:
            pruritus = st.select_slider(
                "Mức độ ngứa:",
                options=[
                    "Không ngứa (0)",
                    "Nhẹ (2/10)",
                    "Trung bình (5/10)",
                    "Nặng (8/10)",
                    "Dữ dội (10/10)",
                ],
                value="Trung bình (5/10)",
                key="d_pru",
            )
            patch_test = st.text_input(
                "Kết quả xét nghiệm áp bì (Patch test):", value="Âm tính", key="d_patch"
            )
            is_contagious = st.checkbox(
                "Có nguy cơ lây nhiễm sang người khác", value=False, key="d_con"
            )

        specialty_data = {
            "lesion_locations": locations,
            "lesion_type": lesion_type,
            "pruritus_level": pruritus,
            "patch_test": patch_test,
            "is_contagious": is_contagious,
        }
    elif selected_dept == "RANG_HAM_MAT":
        c1, c2 = st.columns(2)
        with c1:
            tooth_input = st.text_input(
                "Vị trí răng tổn thương (VD: 36, 46):", "36, 46", key="r_tooth"
            )
            tooth_cond = st.selectbox(
                "Tình trạng tổn thương răng:",
                [
                    "Sâu ngà buốt tủy",
                    "Sâu men răng nhẹ",
                    "Vỡ mẻ thân răng",
                    "Răng khôn mọc lệch đâm R lân cận",
                ],
                key="r_cond",
            )
            tooth_treatment = st.selectbox(
                "Hướng điều trị:",
                [
                    "Hàn trám composite",
                    "Điều trị tủy phục hồi",
                    "Chỉ định nhổ bỏ",
                    "Cắt lợi trùm",
                ],
                key="r_treat",
            )
        with c2:
            tartar = st.slider(
                "Mức độ cao răng (Tartar Grade 0-3):",
                min_value=0,
                max_value=3,
                value=2,
                key="r_tar",
            )
            gingivitis = st.checkbox(
                "Có viêm nướu / Chảy máu chân răng", value=True, key="r_ging"
            )
            hygiene = st.selectbox(
                "Đánh giá vệ sinh răng miệng:",
                ["Kém", "Trung bình", "Tốt"],
                key="r_hyg",
            )

        teeth_list = [
            int(t.strip()) for t in tooth_input.split(",") if t.strip().isdigit()
        ]
        specialty_data = {
            "dental_chart": [
                {
                    "tooth_number": t,
                    "condition": tooth_cond,
                    "treatment": tooth_treatment,
                }
                for t in teeth_list
            ],
            "tartar_grade": tartar,
            "gingivitis": gingivitis,
            "oral_hygiene_score": hygiene,
        }

    st.markdown("---")
    record_group(
        "Kê đơn thuốc",
        "Thông tin thuốc được lưu dưới dạng Embedded Document Array trong MongoDB.",
    )
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        med_name = st.text_input(
            "Tên thuốc:",
            (
                "Amlodipine"
                if selected_dept == "TIM_MACH"
                else ("Fucicort Cream" if selected_dept == "DA_LIEU" else "Rodogyl")
            ),
            key="med_name_create",
        )
    with col_p2:
        med_dose = st.text_input(
            "Hàm lượng/Đơn vị:",
            (
                "5mg"
                if selected_dept == "TIM_MACH"
                else ("Tuýp 15g" if selected_dept == "DA_LIEU" else "Viên nén")
            ),
            key="med_dose_create",
        )
    with col_p3:
        med_qty = st.number_input(
            "Số lượng:",
            min_value=1,
            max_value=100,
            value=30 if selected_dept == "TIM_MACH" else 1,
            key="med_qty_create",
        )
    with col_p4:
        med_usage = st.text_input(
            "Hướng dẫn sử dụng:",
            "Uống 1 viên vào 8h sáng sau ăn",
            key="med_usage_create",
        )

    col_follow1, col_follow2 = st.columns(2)
    with col_follow1:
        follow_up = st.checkbox("Yêu cầu hẹn tái khám", value=True, key="follow_up_chk")
    with col_follow2:
        follow_up_date = (
            st.date_input("Ngày hẹn tái khám", key="follow_up_dt")
            if follow_up
            else None
        )

    if st.button(
        "💾 Xác Nhận & Lưu Bệnh Án Vào MongoDB (qua API)",
        type="primary",
        width="stretch",
        key="btn_save_record",
    ):
        prescriptions = [
            {
                "medicine_name": med_name,
                "dosage": med_dose,
                "quantity": med_qty,
                "usage": med_usage,
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
            "follow_up_date": (
                datetime.combine(follow_up_date, datetime.min.time()).isoformat()
                if follow_up_date
                else None
            ),
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
    record_section(
        "Tra cứu và xem chi tiết bệnh án",
        "Tìm kiếm hồ sơ theo mã bệnh án, thông tin bệnh nhân hoặc chẩn đoán.",
    )

    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        search_query = st.text_input(
            "Tìm kiếm theo Mã bệnh án, Mã BN, Tên bệnh nhân, Chẩn đoán...",
            key="search_record_query",
            placeholder="Nhập từ khóa...",
        )
    with col_s2:
        filter_dept = st.selectbox(
            "Lọc theo chuyên khoa:",
            options=["Tất cả"] + DEPARTMENTS,
            format_func=lambda x: {
                "Tất cả": "Tất cả khoa",
                "TIM_MACH": "Tim Mạch",
                "DA_LIEU": "Da Liễu",
                "RANG_HAM_MAT": "Răng - Hàm - Mặt",
            }.get(x, x),
            key="filter_dept_search",
        )

    try:
        dept_arg = None if filter_dept == "Tất cả" else filter_dept
        records, total_rec = api_get_records(
            skip=0, limit=200, department=dept_arg, search=search_query.strip() or None
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
                        st.markdown(
                            f"**Triệu chứng:** {rec.get('symptoms', 'Không có')}"
                        )
                        st.markdown(f"**Chẩn đoán:** {diag_disp}")
                        st.markdown(
                            f"**Hẹn tái khám:** {'Có' if rec.get('follow_up_required') else 'Không'}"
                        )

                    st.markdown("---")
                    st.markdown(
                        "🩺 **Dữ Liệu Lâm Sàng Đặc Thù (Dynamic Specialty Data):**"
                    )
                    st.json(rec.get("specialty_data", {}))

                    pres_list = rec.get("prescriptions", [])
                    if pres_list:
                        st.markdown("💊 **Đơn Thuốc Đã Kê:**")
                        st.dataframe(pres_list, width="stretch")
        else:
            st.warning(
                "Không tìm thấy hồ sơ bệnh án nào phù hợp với điều kiện tìm kiếm."
            )

    except Exception as e:
        st.error(f"Lỗi khi tra cứu bệnh án: {e}")

# ==========================================
# TAB 3: CHỈNH SỬA HỒ SƠ BỆNH ÁN
# ==========================================
with tab_edit:
    record_section(
        "Chỉnh sửa thông tin bệnh án",
        "Lựa chọn bệnh án cần cập nhật và điều chỉnh thông tin khám bệnh.",
    )
    search_edit = st.text_input(
        "🔍 Tìm bệnh án cần chỉnh sửa (Mã BA, Mã BN, Tên BN):",
        key="search_edit_rec_tab",
    )
    all_recs, _ = api_get_records(
        skip=0, limit=1000, search=search_edit.strip() or None
    )

    if all_recs:
        record_options_edit = {
            f"[{r.get('record_code')}] - BN: {patient_map.get(str(r.get('patient_id')), {}).get('patient_code', 'N/A')} - {patient_map.get(str(r.get('patient_id')), {}).get('full_name', 'N/A')} - Khoa: {r.get('department')}": str(
                r.get("_id") or r.get("id")
            )
            for r in all_recs
        }
        selected_label_edit = st.selectbox(
            "Chọn hồ sơ bệnh án cần sửa:",
            options=list(record_options_edit.keys()),
            key="select_edit_rec_tab",
        )
        chosen_rec_id = record_options_edit[selected_label_edit]

        editing_rec = next(
            (r for r in all_recs if str(r.get("_id") or r.get("id")) == chosen_rec_id),
            None,
        )
        if editing_rec:
            edit_key = str(editing_rec.get("_id") or editing_rec.get("id"))
            old_dept = editing_rec.get("department", "TIM_MACH")
            old_spec_data = editing_rec.get("specialty_data", {})

            record_group(
                "Thông tin hành chính và thăm khám",
                "Cập nhật thông tin cơ bản của phiếu khám bệnh.",
            )
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                e_rec_code = st.text_input(
                    "Mã phiếu khám *",
                    value=editing_rec.get("record_code", ""),
                    key=f"e_code_in_{edit_key}",
                )
                dept_list = DEPARTMENTS
                dept_idx = dept_list.index(old_dept) if old_dept in dept_list else 0

                selected_edit_dept = st.selectbox(
                    "Chuyên khoa khám *",
                    options=dept_list,
                    index=dept_idx,
                    format_func=lambda x: {
                        "TIM_MACH": "Khoa Tim Mạch",
                        "DA_LIEU": "Khoa Da Liễu",
                        "RANG_HAM_MAT": "Khoa Răng - Hàm - Mặt",
                    }.get(x, x),
                    key=f"select_edit_dept_box_{edit_key}",
                )

            with col_e2:
                e_doc_name = st.text_input(
                    "Bác sĩ phụ trách *",
                    value=editing_rec.get("doctor_name", ""),
                    key=f"e_doc_in_{edit_key}",
                )
                e_symptoms = st.text_input(
                    "Lý do khám / Triệu chứng lâm sàng",
                    value=editing_rec.get("symptoms", ""),
                    key=f"e_symp_in_{edit_key}",
                )
                e_diagnosis = st.text_input(
                    "Chẩn đoán bệnh",
                    value=editing_rec.get("diagnosis", ""),
                    key=f"e_diag_in_{edit_key}",
                )

            st.markdown("---")
            st.subheader(
                f"🩺 Dữ Liệu Đặc Thù Của {selected_edit_dept} (Dynamic Schema)"
            )

            updated_specialty_data = {}

            if selected_edit_dept == "TIM_MACH":
                bp = old_spec_data.get("blood_pressure", {})
                sys_val = bp.get("systolic", 140) if isinstance(bp, dict) else 140
                dia_val = bp.get("diastolic", 90) if isinstance(bp, dict) else 90

                tc1, tc2, tc3 = st.columns(3)
                with tc1:
                    systolic = st.number_input(
                        "Huyết áp tâm thu (mmHg):",
                        min_value=60,
                        max_value=250,
                        value=int(sys_val),
                        key=f"edit_tm_sys_{edit_key}",
                    )
                    diastolic = st.number_input(
                        "Huyết áp tâm trương (mmHg):",
                        min_value=40,
                        max_value=150,
                        value=int(dia_val),
                        key=f"edit_tm_dia_{edit_key}",
                    )
                with tc2:
                    heart_rate = st.number_input(
                        "Nhịp tim (lần/phút):",
                        min_value=40,
                        max_value=200,
                        value=int(old_spec_data.get("heart_rate_bpm", 82)),
                        key=f"edit_tm_hr_{edit_key}",
                    )
                    ef = st.number_input(
                        "Chỉ số phân suất tống máu EF (%):",
                        min_value=20,
                        max_value=85,
                        value=int(old_spec_data.get("ejection_fraction_ef", 58)),
                        key=f"edit_tm_ef_{edit_key}",
                    )
                with tc3:
                    ecg_opts = [
                        "Nhịp xoang bình thường",
                        "Nhịp xoang nhanh, ST chênh xuống nhẹ",
                        "Ngoại tâm thu thất rải rác",
                        "Phì đại thất trái",
                    ]
                    cur_ecg = old_spec_data.get("ecg_result", "Nhịp xoang bình thường")
                    ecg_idx = ecg_opts.index(cur_ecg) if cur_ecg in ecg_opts else 0
                    ecg = st.selectbox(
                        "Kết quả Điện tâm đồ (ECG):",
                        ecg_opts,
                        index=ecg_idx,
                        key=f"edit_tm_ecg_{edit_key}",
                    )

                    risk_opts = ["Thấp", "Trung bình", "Cao", "Rất cao"]
                    cur_risk = old_spec_data.get("cardiovascular_risk", "Thấp")
                    risk_idx = risk_opts.index(cur_risk) if cur_risk in risk_opts else 0
                    risk = st.selectbox(
                        "Phân tầng nguy cơ tim mạch:",
                        risk_opts,
                        index=risk_idx,
                        key=f"edit_tm_risk_{edit_key}",
                    )

                updated_specialty_data = {
                    "blood_pressure": {"systolic": systolic, "diastolic": diastolic},
                    "heart_rate_bpm": heart_rate,
                    "ejection_fraction_ef": ef,
                    "ecg_result": ecg,
                    "cardiovascular_risk": risk,
                }

            elif selected_edit_dept == "DA_LIEU":
                dc1, dc2 = st.columns(2)
                with dc1:
                    loc_opts = [
                        "Khuôn mặt",
                        "Cẳng tay",
                        "Bàn tay",
                        "Lưng",
                        "Vùng ngực",
                        "Da đầu",
                        "Cẳng chân",
                    ]
                    cur_locs = old_spec_data.get("lesion_locations", ["Cẳng tay"])
                    valid_locs = (
                        [l for l in cur_locs if l in loc_opts]
                        if isinstance(cur_locs, list)
                        else ["Cẳng tay"]
                    )
                    locations = st.multiselect(
                        "Vị trí tổn thương da:",
                        loc_opts,
                        default=valid_locs if valid_locs else ["Cẳng tay"],
                        key=f"edit_dl_loc_{edit_key}",
                    )

                    les_opts = [
                        "Mảng hồng ban giới hạn rõ",
                        "Sẩn viêm, mụn mủ hoại tử",
                        "Mụn nước mọc thành chùm rải rác",
                        "Vảy nến bong tróc màu bạc",
                        "Mảng thâm sạm tăng sắc tố",
                    ]
                    cur_les = old_spec_data.get(
                        "lesion_type", "Mảng hồng ban giới hạn rõ"
                    )
                    les_idx = les_opts.index(cur_les) if cur_les in les_opts else 0
                    lesion_type = st.selectbox(
                        "Loại thương tổn đặc trưng:",
                        les_opts,
                        index=les_idx,
                        key=f"edit_dl_les_{edit_key}",
                    )
                with dc2:
                    pru_opts = [
                        "Không ngứa (0)",
                        "Nhẹ (2/10)",
                        "Trung bình (5/10)",
                        "Nặng (8/10)",
                        "Dữ dội (10/10)",
                    ]
                    cur_pru = old_spec_data.get("pruritus_level", "Trung bình (5/10)")
                    pruritus = st.select_slider(
                        "Mức độ ngứa:",
                        options=pru_opts,
                        value=cur_pru if cur_pru in pru_opts else "Trung bình (5/10)",
                        key=f"edit_dl_pru_{edit_key}",
                    )

                    patch_test = st.text_input(
                        "Kết quả xét nghiệm áp bì (Patch test):",
                        value=old_spec_data.get("patch_test", "Âm tính"),
                        key=f"edit_dl_patch_{edit_key}",
                    )
                    is_contagious = st.checkbox(
                        "Có nguy cơ lây nhiễm sang người khác",
                        value=bool(old_spec_data.get("is_contagious", False)),
                        key=f"edit_dl_con_{edit_key}",
                    )

                updated_specialty_data = {
                    "lesion_locations": locations,
                    "lesion_type": lesion_type,
                    "pruritus_level": pruritus,
                    "patch_test": patch_test,
                    "is_contagious": is_contagious,
                }

            elif selected_edit_dept == "RANG_HAM_MAT":
                chart = old_spec_data.get("dental_chart", [])
                default_teeth_str = (
                    ", ".join([str(t.get("tooth_number")) for t in chart])
                    if chart
                    else "36, 46"
                )

                c1, c2 = st.columns(2)
                with c1:
                    tooth_input = st.text_input(
                        "Vị trí răng tổn thương (cách nhau dấu phẩy, VD: 36, 46):",
                        value=default_teeth_str,
                        key=f"edit_rhm_teeth_{edit_key}",
                    )

                    cond_opts = [
                        "Sâu ngà buốt tủy",
                        "Sâu men răng nhẹ",
                        "Vỡ mẻ thân răng",
                        "Răng khôn mọc lệch đâm R lân cận",
                    ]
                    cur_cond = (
                        chart[0].get("condition", "Sâu ngà buốt tủy")
                        if chart
                        else "Sâu ngà buốt tủy"
                    )
                    cond_idx = cond_opts.index(cur_cond) if cur_cond in cond_opts else 0
                    tooth_cond = st.selectbox(
                        "Tình trạng tổn thương răng:",
                        cond_opts,
                        index=cond_idx,
                        key=f"edit_rhm_cond_{edit_key}",
                    )

                    treat_opts = [
                        "Hàn trám composite",
                        "Điều trị tủy phục hồi",
                        "Chỉ định nhổ bỏ",
                        "Cắt lợi trùm",
                    ]
                    cur_treat = (
                        chart[0].get("treatment", "Hàn trám composite")
                        if chart
                        else "Hàn trám composite"
                    )
                    treat_idx = (
                        treat_opts.index(cur_treat) if cur_treat in treat_opts else 0
                    )
                    tooth_treatment = st.selectbox(
                        "Hướng điều trị:",
                        treat_opts,
                        index=treat_idx,
                        key=f"edit_rhm_treat_{edit_key}",
                    )
                with c2:
                    tartar = st.slider(
                        "Mức độ cao răng (Tartar Grade 0-3):",
                        min_value=0,
                        max_value=3,
                        value=int(old_spec_data.get("tartar_grade", 2)),
                        key=f"edit_rhm_tar_{edit_key}",
                    )
                    gingivitis = st.checkbox(
                        "Có viêm nướu / Chảy máu chân răng",
                        value=bool(old_spec_data.get("gingivitis", True)),
                        key=f"edit_rhm_ging_{edit_key}",
                    )

                    hyg_opts = ["Kém", "Trung bình", "Tốt"]
                    cur_hyg = old_spec_data.get("oral_hygiene_score", "Trung bình")
                    hyg_idx = hyg_opts.index(cur_hyg) if cur_hyg in hyg_opts else 1
                    hygiene = st.selectbox(
                        "Đánh giá vệ sinh răng miệng:",
                        hyg_opts,
                        index=hyg_idx,
                        key=f"edit_rhm_hyg_{edit_key}",
                    )

                teeth_list = [
                    int(t.strip())
                    for t in tooth_input.split(",")
                    if t.strip().isdigit()
                ]
                updated_specialty_data = {
                    "dental_chart": [
                        {
                            "tooth_number": t,
                            "condition": tooth_cond,
                            "treatment": tooth_treatment,
                        }
                        for t in teeth_list
                    ],
                    "tartar_grade": tartar,
                    "gingivitis": gingivitis,
                    "oral_hygiene_score": hygiene,
                }

            st.markdown("---")
            e_follow_up = st.checkbox(
                "Yêu cầu hẹn tái khám",
                value=bool(editing_rec.get("follow_up_required", False)),
                key=f"e_follow_chk_{edit_key}",
            )

            if st.button(
                "💾 Lưu Cập Nhật Bệnh Án",
                type="primary",
                width="stretch",
                key=f"btn_update_rec_{edit_key}",
            ):
                update_payload = {
                    "record_code": e_rec_code,
                    "department": selected_edit_dept,
                    "doctor_name": e_doc_name,
                    "symptoms": e_symptoms,
                    "diagnosis": e_diagnosis,
                    "specialty_data": updated_specialty_data,
                    "follow_up_required": e_follow_up,
                }
                try:
                    res, status_code = api_update_record(chosen_rec_id, update_payload)
                    if status_code == 200:
                        st.toast(
                            "Cập nhật thành công hồ sơ bệnh án và dữ liệu đặc thù!",
                            icon="✅",
                        )
                        st.success(
                            "Cập nhật thành công hồ sơ bệnh án và dữ liệu đặc thù!"
                        )
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
    record_section(
        "Xóa hồ sơ bệnh án", "Tìm kiếm và xác nhận hồ sơ bệnh án cần xóa khỏi hệ thống."
    )
    search_del = st.text_input(
        "🔍 Tìm bệnh án cần xóa (Mã BA, Mã BN, Tên BN):", key="search_del_rec_tab"
    )
    recs_del, _ = api_get_records(skip=0, limit=1000, search=search_del.strip() or None)

    if recs_del:
        record_options_del = {
            f"[{r.get('record_code')}] - BN: {patient_map.get(str(r.get('patient_id')), {}).get('patient_code', 'N/A')} - {patient_map.get(str(r.get('patient_id')), {}).get('full_name', 'N/A')} - Khoa: {r.get('department')}": str(
                r.get("_id") or r.get("id")
            )
            for r in recs_del
        }
        selected_label_del = st.selectbox(
            "Chọn hồ sơ bệnh án cần xóa:",
            options=list(record_options_del.keys()),
            key="select_del_rec_tab",
        )
        chosen_del_rec_id = record_options_del[selected_label_del]

        target_rec = next(
            (
                r
                for r in recs_del
                if str(r.get("_id") or r.get("id")) == chosen_del_rec_id
            ),
            None,
        )
        if target_rec:
            st.warning(
                f"⚠️ Bạn có chắc chắn muốn xóa vĩnh viễn phiếu khám mã **{target_rec.get('record_code')}** của bệnh nhân **{patient_map.get(str(target_rec.get('patient_id')), {}).get('full_name', 'N/A')}** không?"
            )
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
