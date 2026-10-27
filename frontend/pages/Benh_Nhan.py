import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import re
from html import escape

# ============================================================
# 1. CẤU HÌNH VÀ KẾT NỐI API HIỆN TẠI
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

from frontend.api_client import (
    api_get_patients,
    api_create_patient,
    api_update_patient,
    api_delete_patient,
)

st.set_page_config(
    page_title="Quản lý bệnh nhân | MediSpace", page_icon="", layout="wide"
)


# ============================================================
# 2. CSS GIAO DIỆN
# Chỉ thay đổi hiển thị, không ảnh hưởng backend
# ============================================================

st.markdown(
    """
<style>
    :root {
        --patient-primary: #167D70;
        --patient-primary-dark: #10665B;
        --patient-soft: #E8F5F2;
        --patient-bg: #F5F8FA;
        --patient-heading: #203B49;
        --patient-text: #526672;
        --patient-border: #E1E9ED;
    }

    .stApp {
        background-color: var(--patient-bg);
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    /* HEADER */
    .patient-header {
        background: linear-gradient(
            115deg,
            #FFFFFF 0%,
            #E8F5F2 100%
        );
        border: 1px solid #DCEBE7;
        border-radius: 18px;
        padding: 32px 36px;
        margin-bottom: 24px;
    }

    .patient-eyebrow {
        color: #167D70;
        font-size: 12px;
        letter-spacing: 1.4px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .patient-title {
        color: #203B49;
        font-size: clamp(28px, 3vw, 38px);
        font-weight: 750;
        margin: 0 0 10px;
    }

    .patient-description {
        color: #526672;
        font-size: 14px;
        line-height: 1.8;
        margin: 0;
    }

    /* THẺ THỐNG KÊ */
    .patient-summary {
        background: #FFFFFF;
        border: 1px solid #E1E9ED;
        border-radius: 14px;
        padding: 22px 25px;
        margin-bottom: 18px;
        min-height: 127px;
    }

    .patient-summary-label {
        color: #526672;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 9px;
    }

    .patient-summary-number {
        color: #203B49;
        font-size: 30px;
        font-weight: 750;
        line-height: 1.25;
    }

    .patient-summary-note {
        color: #80909A;
        font-size: 12px;
        margin-top: 6px;
    }

    /* TIÊU ĐỀ KHU VỰC */
    .patient-section {
        margin: 16px 0;
    }

    .patient-section-title {
        color: #203B49;
        font-size: 21px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .patient-section-desc {
        color: #80909A;
        font-size: 13px;
        line-height: 1.7;
    }

    /* TAB */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #FFFFFF;
        border: 1px solid #E1E9ED;
        border-radius: 13px;
        padding: 7px;
        margin-bottom: 20px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 9px;
        color: #526672;
        font-weight: 600;
        font-size: 13px;
        padding: 10px 18px;
    }

    .stTabs [aria-selected="true"] {
        background: #E8F5F2 !important;
        color: #167D70 !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        background: transparent;
    }

    /* INPUT */
    .stTextInput input,
    .stDateInput input,
    .stSelectbox [data-baseweb="select"] > div {
        border-radius: 9px;
    }

    .stTextInput input:focus,
    .stDateInput input:focus {
        border-color: #167D70;
    }

    /* LABEL */
    .stTextInput label,
    .stSelectbox label,
    .stDateInput label {
        color: #203B49;
        font-weight: 600;
        font-size: 13px;
    }

    /* FORM */
    [data-testid="stForm"] {
        background: #FFFFFF;
        border: 1px solid #E1E9ED;
        border-radius: 15px;
        padding: 25px;
    }

    /* BUTTON */
    .stButton > button,
    .stFormSubmitButton > button {
        border-radius: 9px;
        font-weight: 600;
        min-height: 40px;
        transition: all 0.2s ease;
    }

    .stFormSubmitButton > button {
        background: #167D70;
        color: white;
        border-color: #167D70;
    }

    .stFormSubmitButton > button:hover {
        background: #10665B;
        color: white;
        border-color: #10665B;
    }

    /* BẢNG DỮ LIỆU */
    [data-testid="stDataFrame"] {
        border: 1px solid #E1E9ED;
        border-radius: 12px;
        overflow: hidden;
    }

    /* THẺ CHÚ THÍCH */
    .patient-note {
        background: #E8F5F2;
        border: 1px solid #D5EBE5;
        border-radius: 11px;
        padding: 14px 18px;
        margin: 14px 0 18px;
        color: #167D70;
        font-size: 13px;
        line-height: 1.7;
    }

    /* CẢNH BÁO XÓA */
    .patient-danger-title {
        font-size: 18px;
        font-weight: 700;
        color: #9D3E3E;
        margin-bottom: 8px;
    }

    .patient-danger-note {
        color: #805A4B;
        font-size: 13px;
        line-height: 1.8;
    }

    /* FOOTER */
    .patient-footer {
        margin-top: 36px;
        padding: 18px 0;
        border-top: 1px solid #E1E9ED;
        color: #80909A;
        font-size: 12px;
        text-align: center;
    }

    @media (max-width: 768px) {
        .patient-header {
            padding: 23px;
        }

        [data-testid="stForm"] {
            padding: 15px;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 8px;
            font-size: 12px;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# MEDISPACE PATIENT MANAGEMENT - UI V2
# Chỉ bổ sung ảnh và hiệu ứng
# Không thay đổi API, CRUD hoặc luồng xử lý
# ============================================================

import base64

# Ảnh vector hồ sơ bệnh nhân được nhúng trực tiếp vào CSS.
# Không cần tạo file ảnh hoặc kết nối Internet.

patient_hero_svg = """
<svg xmlns="http://www.w3.org/2000/svg"
     width="500" height="340"
     viewBox="0 0 500 340" fill="none">

<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop stop-color="#FFFFFF"/>
    <stop offset="1" stop-color="#E8F5F2"/>
  </linearGradient>
  <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%">
    <feDropShadow dx="0" dy="10" stdDeviation="12"
      flood-color="#167D70" flood-opacity="0.13"/>
  </filter>
</defs>

<circle cx="255" cy="170" r="138"
  fill="#CDEBE5" opacity=".55"/>

<circle cx="420" cy="70" r="25"
  fill="#B5DDD5" opacity=".65"/>

<circle cx="80" cy="270" r="16"
  fill="#A4D8CE" opacity=".5"/>

<!-- Hồ sơ bệnh nhân -->
<rect x="120" y="45" width="255" height="260" rx="18"
  fill="url(#bg)" stroke="#C5E2DC" stroke-width="2"
  filter="url(#shadow)"/>

<path d="M120 64 Q120 45 139 45 H356 Q375 45 375 64 V101 H120 Z"
  fill="#167D70"/>

<rect x="146" y="65" width="110" height="11" rx="5"
  fill="#FFFFFF" opacity=".85"/>

<!-- Ảnh đại diện cách điệu -->
<rect x="145" y="124" width="88" height="98" rx="15"
  fill="#DBF0EB"/>

<circle cx="189" cy="155" r="18" fill="#65B8A9"/>

<path d="M158 199 C158 175 220 175 220 199 V210 H158 Z"
  fill="#167D70"/>

<!-- Các trường thông tin -->
<rect x="250" y="132" width="92" height="9" rx="4"
  fill="#8EC8BC"/>

<rect x="250" y="153" width="75" height="7" rx="3"
  fill="#B6DAD2"/>

<rect x="250" y="172" width="86" height="7" rx="3"
  fill="#B6DAD2"/>

<rect x="250" y="191" width="62" height="7" rx="3"
  fill="#B6DAD2"/>

<path d="M147 247 H345"
  stroke="#D0E7E1" stroke-width="2"/>

<rect x="147" y="259" width="130" height="8" rx="4"
  fill="#A4D0C6"/>

<rect x="147" y="277" width="88" height="7" rx="3"
  fill="#C0DED7"/>

<!-- Thẻ nổi thứ nhất -->
<rect x="48" y="125" width="105" height="102" rx="15"
  fill="#FFFFFF" stroke="#D6EAE5"
  filter="url(#shadow)"/>

<rect x="64" y="145" width="72" height="9" rx="4"
  fill="#167D70" opacity=".8"/>

<rect x="64" y="165" width="57" height="7" rx="3"
  fill="#A9D4CA"/>

<rect x="64" y="183" width="68" height="7" rx="3"
  fill="#A9D4CA"/>

<rect x="64" y="201" width="40" height="7" rx="3"
  fill="#A9D4CA"/>

<!-- Thẻ nổi thứ hai -->
<rect x="357" y="195" width="102" height="89" rx="14"
  fill="#FFFFFF" stroke="#D6EAE5"
  filter="url(#shadow)"/>

<rect x="372" y="212" width="70" height="8" rx="4"
  fill="#167D70" opacity=".75"/>

<rect x="372" y="233" width="55" height="7" rx="3"
  fill="#A9D4CA"/>

<rect x="372" y="250" width="65" height="7" rx="3"
  fill="#A9D4CA"/>

</svg>
"""

patient_hero_b64 = base64.b64encode(patient_hero_svg.encode("utf-8")).decode("utf-8")


# CSS bổ sung độc lập, nạp sau CSS hiện tại.
patient_v2_css = """
<style>

/* =========================================
   1. HEADER CÓ ẢNH MINH HỌA
   ========================================= */

.patient-header {
    position: relative;
    isolation: isolate;
    min-height: 260px;
    padding: 35px 39% 35px 38px;

    background: linear-gradient(
        115deg,
        #FFFFFF 0%,
        #E8F5F2 55%,
        #D6EDE7 100%
    );

    background-size: 200% 200%;
    animation: patientGradient 15s ease-in-out infinite;

    overflow: hidden;
}

/* Ảnh vector nằm trong lớp CSS,
   không làm ảnh hưởng nội dung Header */

.patient-header::after {
    content: "";
    position: absolute;
    z-index: 1;

    width: 38%;
    max-width: 420px;
    height: 265px;

    right: 10px;
    top: 50%;

    background-image: url("data:image/svg+xml;base64,__PATIENT_IMAGE__");
    background-position: center;
    background-repeat: no-repeat;
    background-size: contain;

    transform: translateY(-50%);
    animation: patientFloat 6s ease-in-out infinite;

    pointer-events: none;
}

/* Vòng sáng nền */

.patient-header::before {
    content: "";
    position: absolute;

    width: 270px;
    height: 270px;
    right: 4%;
    bottom: -135px;

    border-radius: 50%;

    background: radial-gradient(
        circle,
        rgba(85,185,174,0.25),
        rgba(85,185,174,0)
    );

    animation: patientGlow 9s ease-in-out infinite;
    pointer-events: none;
}

/* Đảm bảo nội dung không bị ảnh che */

.patient-header > * {
    position: relative;
    z-index: 2;
}

.patient-title {
    font-size: clamp(28px, 3vw, 39px);
    line-height: 1.25;
    letter-spacing: -0.5px;
}

.patient-description {
    max-width: 670px;
    line-height: 1.8;
}


/* =========================================
   2. THẺ TỔNG SỐ BỆNH NHÂN
   ========================================= */

.patient-summary {
    position: relative;
    overflow: hidden;

    background: linear-gradient(
        120deg,
        #FFFFFF 0%,
        #F1FAF8 100%
    );

    border: 1px solid #DCEBE7;
    border-radius: 15px;

    box-shadow:
        0 5px 20px rgba(32,59,73,0.04);

    transition:
        transform 0.3s ease,
        box-shadow 0.3s ease,
        border-color 0.3s ease;
}

/* Thanh xanh phía trên */

.patient-summary::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    height: 4px;
    width: 100%;

    background: linear-gradient(
        90deg,
        #167D70,
        #55B9AE
    );
}

/* Vòng tròn trang trí */

.patient-summary::after {
    content: "";
    position: absolute;

    width: 130px;
    height: 130px;
    right: -35px;
    bottom: -55px;

    border-radius: 50%;
    background: rgba(22,125,112,0.055);

    pointer-events: none;
}
.patient-summary-mark {
    position: absolute;
    right: 22px;
    bottom: 10px;

    font-size: 72px;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -3px;

    color: rgba(22,125,112,0.07);

    pointer-events: none;
    user-select: none;
    z-index: 0;
}

.patient-summary-label,
.patient-summary-number,
.patient-summary-note {
    position: relative;
    z-index: 1;
}

.patient-summary:hover {
    transform: translateY(-5px);
    border-color: #B7DED5;

    box-shadow:
        0 15px 30px rgba(22,125,112,0.11);
}

.patient-summary-number {
    color: #167D70;
    font-size: 36px;
    transition: transform 0.3s ease;
}

.patient-summary:hover .patient-summary-number {
    transform: translateX(3px);
}


/* =========================================
   3. THANH TAB CHỨC NĂNG
   ========================================= */

.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF;
    border: 1px solid #E1E9ED;
    border-radius: 14px;

    padding: 8px;
    gap: 8px;

    box-shadow:
        0 4px 16px rgba(32,59,73,0.025);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 9px;

    transition:
        background-color 0.25s ease,
        color 0.25s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    background: #F0F8F6;
    color: #167D70;
}

.stTabs [aria-selected="true"] {
    background: #E8F5F2 !important;
    color: #167D70 !important;
    font-weight: 700;
}


/* =========================================
   4. FORM THÊM VÀ CHỈNH SỬA
   ========================================= */

[data-testid="stForm"] {
    background: linear-gradient(
        180deg,
        #FFFFFF,
        #FCFEFD
    );

    border: 1px solid #E1E9ED;
    border-radius: 16px;

    box-shadow:
        0 5px 20px rgba(32,59,73,0.035);

    transition:
        border-color 0.3s ease,
        box-shadow 0.3s ease;
}

[data-testid="stForm"]:hover {
    border-color: #B7DED5;

    box-shadow:
        0 9px 26px rgba(22,125,112,0.06);
}

/* Input focus */

.stTextInput input:focus,
.stDateInput input:focus {
    border-color: #167D70;
    box-shadow:
        0 0 0 1px rgba(22,125,112,0.15);
}

/* Nút thao tác */

.stButton > button,
.stFormSubmitButton > button {
    transition:
        background-color 0.25s ease,
        box-shadow 0.25s ease,
        transform 0.25s ease;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    transform: translateY(-2px);

    box-shadow:
        0 6px 15px rgba(22,125,112,0.11);
}


/* =========================================
   5. BẢNG DANH SÁCH BỆNH NHÂN
   ========================================= */

[data-testid="stDataFrame"] {
    background: #FFFFFF;
    border-radius: 14px;
    border: 1px solid #E1E9ED;

    box-shadow:
        0 5px 20px rgba(32,59,73,0.035);

    transition:
        box-shadow 0.3s ease,
        border-color 0.3s ease;
}

[data-testid="stDataFrame"]:hover {
    border-color: #B7DED5;

    box-shadow:
        0 10px 26px rgba(22,125,112,0.075);
}


/* =========================================
   6. GHI CHÚ VÀ CẢNH BÁO
   ========================================= */

.patient-note {
    position: relative;
    overflow: hidden;

    background: linear-gradient(
        110deg,
        #E8F5F2,
        #F2FAF8
    );

    border-color: #D1E8E1;
    border-radius: 12px;

    transition:
        border-color 0.25s ease;
}

.patient-note:hover {
    border-color: #A8D8CD;
}

/* Cảnh báo xóa: không thay đổi thao tác */

.patient-danger-title {
    color: #A64C4C;
    letter-spacing: -0.2px;
}


/* =========================================
   7. HIỆU ỨNG
   ========================================= */

@keyframes patientGradient {
    0%, 100% {
        background-position: 0% 50%;
    }

    50% {
        background-position: 100% 50%;
    }
}

@keyframes patientFloat {
    0%, 100% {
        transform: translateY(-50%);
    }

    50% {
        transform: translateY(calc(-50% - 7px));
    }
}

@keyframes patientGlow {
    0%, 100% {
        opacity: 0.4;
        transform: scale(1);
    }

    50% {
        opacity: 0.8;
        transform: scale(1.12);
    }
}


/* =========================================
   8. RESPONSIVE
   ========================================= */

@media (max-width: 1000px) {
    .patient-header {
        padding-right: 34%;
    }

    .patient-header::after {
        width: 34%;
    }
}

@media (max-width: 760px) {
    .patient-header {
        min-height: 0;
        padding: 25px 23px;
    }

    .patient-header::after {
        display: none;
    }

    .patient-summary-number {
        font-size: 30px;
    }
}

/* Tôn trọng cài đặt giảm chuyển động */

@media (prefers-reduced-motion: reduce) {
    .patient-header,
    .patient-header::before,
    .patient-header::after {
        animation: none !important;
    }

    .patient-summary,
    .patient-summary-number,
    [data-testid="stForm"],
    [data-testid="stDataFrame"],
    .patient-note,
    .stButton > button,
    .stFormSubmitButton > button {
        transition: none !important;
    }
}

</style>
"""

# Chèn ảnh vào CSS
patient_v2_css = patient_v2_css.replace("__PATIENT_IMAGE__", patient_hero_b64)

st.markdown(patient_v2_css, unsafe_allow_html=True)

# ============================================================
# 3. HÀM HIỂN THỊ HTML
# Tránh lỗi Streamlit hiển thị HTML thành code
# ============================================================


def render_html(html):
    cleaned_html = "\n".join(line.lstrip() for line in html.splitlines()).strip()

    st.markdown(cleaned_html, unsafe_allow_html=True)


def format_number(value):
    try:
        return f"{int(value):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "—"


# ============================================================
# 4. HEADER
# ============================================================

render_html("""
<div class="patient-header">
    <div class="patient-eyebrow">
        MEDISPACE · PATIENT MANAGEMENT
    </div>

    <h1 class="patient-title">
        Quản lý bệnh nhân
    </h1>

    <p class="patient-description">
        Quản lý thông tin hành chính bệnh nhân,
        tìm kiếm hồ sơ, thêm mới và cập nhật
        dữ liệu thông qua hệ thống MediSpace.
    </p>
</div>
""")


# ============================================================
# 5. KẾT NỐI BACKEND - GIỮ NGUYÊN
# ============================================================

try:
    _, total_all = api_get_patients(skip=0, limit=1000)
except Exception:
    st.error(
        "Không kết nối được FastAPI Backend. "
        "Hãy kiểm tra backend đang chạy ở cổng 8000."
    )
    st.stop()


# ============================================================
# 6. THẺ THỐNG KÊ
# ============================================================

render_html(f"""
<div class="patient-section">
    <div class="patient-section-title">
        Tổng quan bệnh nhân
    </div>
    <div class="patient-section-desc">
        Thông tin tổng hợp từ cơ sở dữ liệu hiện tại.
    </div>
</div>

<div class="patient-summary">
    <div class="patient-summary-mark">
        BN
    </div>

    <div class="patient-summary-label">
        Tổng số bệnh nhân
    </div>

    <div class="patient-summary-number">
        {format_number(total_all)}
    </div>

    <div class="patient-summary-note">
        Hồ sơ bệnh nhân đang được quản lý trong MediSpace
    </div>
</div>
""")


# ============================================================
# 7. BỐN TAB CHỨC NĂNG - GIỮ NGUYÊN LUỒNG
# ============================================================

tab_list, tab_create, tab_edit, tab_delete = st.tabs(
    ["Danh sách bệnh nhân", "Thêm bệnh nhân", "Chỉnh sửa bệnh nhân", "Xóa bệnh nhân"]
)


# ============================================================
# TAB 1 - DANH SÁCH BỆNH NHÂN
# ============================================================

with tab_list:

    render_html("""
    <div class="patient-section">
        <div class="patient-section-title">
            Danh sách bệnh nhân
        </div>
        <div class="patient-section-desc">
            Tra cứu hồ sơ theo họ tên, mã bệnh nhân
            hoặc số điện thoại.
        </div>
    </div>
    """)

    c_search, c_limit = st.columns([3, 1])

    with c_search:
        search_query = st.text_input(
            "Tìm kiếm bệnh nhân",
            placeholder="Nhập họ tên, mã bệnh nhân hoặc số điện thoại...",
            key="search_tab_1",
        )

    with c_limit:
        limit_val = st.selectbox("Hiển thị tối đa", [100, 200, 500, "Tất cả"], index=1)

        actual_limit = 10000 if limit_val == "Tất cả" else limit_val

    patients, total = api_get_patients(
        skip=0, limit=actual_limit, search=search_query if search_query else None
    )

    render_html(f"""
    <div class="patient-note">
        Đang hiển thị <b>{len(patients)}</b>
        trên tổng số <b>{format_number(total)}</b>
        hồ sơ bệnh nhân phù hợp.
    </div>
    """)

    if patients:
        table_data = []

        for p in patients:
            table_data.append(
                {
                    "ID Hệ Thống": str(p.get("_id") or p.get("id")),
                    "Mã BN": p.get("patient_code"),
                    "Họ và Tên": p.get("full_name"),
                    "Ngày sinh": p.get("dob"),
                    "Giới tính": p.get("gender"),
                    "Điện thoại": p.get("phone"),
                    "Nhóm máu": p.get("blood_group"),
                    "Dị ứng": (
                        ", ".join(p.get("allergies", []))
                        if p.get("allergies")
                        else "Không"
                    ),
                    "Địa chỉ": p.get("address"),
                }
            )

        df = pd.DataFrame(table_data)

        st.dataframe(
            df.drop(columns=["ID Hệ Thống"]),
            width="stretch",
            hide_index=True,
            height=450,
        )

    else:
        st.warning(
            "Chưa có hồ sơ bệnh nhân nào hoặc " "không tìm thấy kết quả phù hợp."
        )


# ============================================================
# TAB 2 - THÊM BỆNH NHÂN
# ============================================================

with tab_create:

    render_html("""
    <div class="patient-section">
        <div class="patient-section-title">
            Thêm bệnh nhân mới
        </div>
        <div class="patient-section-desc">
            Nhập thông tin hành chính để tạo hồ sơ bệnh nhân.
        </div>
    </div>
    """)

    render_html("""
    <div class="patient-note">
        Những trường có dấu * là thông tin bắt buộc.
        Vui lòng kiểm tra thông tin trước khi lưu.
    </div>
    """)

    with st.form("form_create_patient"):

        st.markdown("#### Thông tin bệnh nhân")

        c1, c2 = st.columns(2, gap="large")

        with c1:
            p_code = st.text_input("Mã bệnh nhân *", value=f"BN-{total_all + 1:04d}")

            raw_p_name = st.text_input(
                "Họ và tên *", placeholder="Ví dụ: Nguyễn Văn An"
            )

            p_dob = st.date_input("Ngày sinh")

            p_gender = st.selectbox("Giới tính *", ["Nam", "Nữ", "Khác"])

        with c2:
            col_code, col_num = st.columns([1, 3])

            with col_code:
                st.text_input(
                    "Mã quốc gia", value="+84", disabled=True, key="prefix_add"
                )

            with col_num:
                p_phone_suffix = st.text_input(
                    "Số điện thoại (không cần nhập số 0 ở đầu) *",
                    placeholder="912345678",
                    max_chars=10,
                )

            p_blood = st.selectbox(
                "Nhóm máu",
                ["Chưa xác định", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"],
            )

            p_allergies = st.text_input(
                "Dị ứng (cách nhau bởi dấu phẩy)",
                placeholder="Ví dụ: Penicillin, Hải sản",
            )

            p_address = st.text_input(
                "Địa chỉ thường trú", placeholder="Số nhà, đường, quận/huyện, tỉnh/TP"
            )

        st.divider()

        submitted = st.form_submit_button(
            "Lưu hồ sơ bệnh nhân", type="primary", use_container_width=True
        )

        if submitted:
            cleaned_name = raw_p_name.strip()
            phone_body = p_phone_suffix.strip()

            if phone_body.startswith("0"):
                phone_body = phone_body[1:]

            vietnamese_name_regex = (
                r"^[a-zA-Zàáảãạăằắẳẵặâầấẩẫậ"
                r"èéẻẽẹêềếểễệìíỉĩịòóỏõọ"
                r"ôồốổỗộơờớởỡợùúủũụưừứ"
                r"ửữựỳýỷỹỵĐđ\s]+$"
            )

            if not p_code or not cleaned_name:
                st.error("Vui lòng điền đầy đủ Mã bệnh nhân và Họ tên.")

            elif not re.match(vietnamese_name_regex, cleaned_name):
                st.error(
                    "Họ và tên chỉ được chứa chữ cái, "
                    "không được nhập số hoặc ký tự đặc biệt!"
                )

            elif not phone_body.isdigit() or not (9 <= len(phone_body) <= 10):
                st.error(
                    "Số điện thoại không hợp lệ! "
                    "Chỉ được nhập số (9-10 chữ số tiếp theo sau +84)."
                )

            else:
                full_phone = f"+84{phone_body}"
                formatted_name = cleaned_name.title()

                try:
                    allergies_list = (
                        [a.strip() for a in p_allergies.split(",") if a.strip()]
                        if p_allergies
                        else []
                    )

                    new_patient_data = {
                        "patient_code": p_code,
                        "full_name": formatted_name,
                        "dob": str(p_dob),
                        "gender": p_gender,
                        "phone": full_phone,
                        "address": p_address,
                        "blood_group": (
                            p_blood if p_blood != "Chưa xác định" else None
                        ),
                        "allergies": allergies_list,
                    }

                    res, status_code = api_create_patient(new_patient_data)

                    if status_code in [200, 201]:
                        st.toast(f"Tạo bệnh nhân {formatted_name} thành công!")

                        st.success(f"Tạo bệnh nhân thành công! " f"Mã BN: `{p_code}`")

                        st.rerun()

                    else:
                        st.error(f"Lỗi từ API: {res}")

                except Exception as e:
                    st.error(f"Lỗi kết nối API: {e}")


# ============================================================
# TAB 3 - CHỈNH SỬA BỆNH NHÂN
# ============================================================

with tab_edit:

    render_html("""
    <div class="patient-section">
        <div class="patient-section-title">
            Chỉnh sửa thông tin bệnh nhân
        </div>
        <div class="patient-section-desc">
            Tìm kiếm và lựa chọn hồ sơ trước khi cập nhật.
        </div>
    </div>
    """)

    search_edit = st.text_input(
        "Tìm kiếm bệnh nhân cần sửa (Họ tên, Mã BN, SĐT)",
        placeholder="Nhập thông tin bệnh nhân cần chỉnh sửa...",
        key="search_edit_tab",
    )

    patients_edit, _ = api_get_patients(
        skip=0, limit=1000, search=search_edit if search_edit else None
    )

    if patients_edit:

        patient_options_edit = {
            (
                f"{p.get('patient_code')} - "
                f"{p.get('full_name')} "
                f"({p.get('phone', 'Không có SĐT')})"
            ): str(p.get("_id") or p.get("id"))
            for p in patients_edit
        }

        selected_label_edit = st.selectbox(
            "Chọn bệnh nhân từ kết quả tìm kiếm",
            options=list(patient_options_edit.keys()),
            key="select_edit_tab",
        )

        chosen_id_edit = (
            patient_options_edit[selected_label_edit] if selected_label_edit else None
        )

        editing_p = next(
            (
                p
                for p in patients_edit
                if str(p.get("_id") or p.get("id")) == chosen_id_edit
            ),
            None,
        )

        if editing_p:

            render_html(f"""
            <div class="patient-note">
                Đang chỉnh sửa hồ sơ:
                <b>{escape(str(editing_p.get("full_name", "")))}</b>
                · Mã bệnh nhân:
                <b>{escape(str(editing_p.get("patient_code", "")))}</b>
            </div>
            """)

            old_phone = editing_p.get("phone", "")

            if old_phone.startswith("+84"):
                old_phone_suffix = old_phone[3:]

            elif old_phone.startswith("0"):
                old_phone_suffix = old_phone[1:]

            else:
                old_phone_suffix = old_phone

            with st.form("form_edit_patient_tab"):

                st.markdown("#### Cập nhật hồ sơ bệnh nhân")

                ec1, ec2 = st.columns(2, gap="large")

                with ec1:

                    e_code = st.text_input(
                        "Mã bệnh nhân *", value=editing_p.get("patient_code", "")
                    )

                    raw_e_name = st.text_input(
                        "Họ và tên *", value=editing_p.get("full_name", "")
                    )

                    try:
                        default_dob = pd.to_datetime(editing_p.get("dob")).date()

                    except:
                        default_dob = pd.to_datetime("2000-01-01").date()

                    e_dob = st.date_input("Ngày sinh", value=default_dob)

                    gender_options = ["Nam", "Nữ", "Khác"]

                    g_idx = (
                        gender_options.index(editing_p.get("gender"))
                        if editing_p.get("gender") in gender_options
                        else 0
                    )

                    e_gender = st.selectbox("Giới tính *", gender_options, index=g_idx)

                with ec2:

                    col_e_code, col_e_num = st.columns([1, 3])

                    with col_e_code:
                        st.text_input(
                            "Mã quốc gia", value="+84", disabled=True, key="prefix_edit"
                        )

                    with col_e_num:
                        e_phone_suffix = st.text_input(
                            "Số điện thoại (không cần nhập số 0 ở đầu) *",
                            value=old_phone_suffix,
                            max_chars=10,
                        )

                    blood_options = [
                        "Chưa xác định",
                        "A+",
                        "A-",
                        "B+",
                        "B-",
                        "O+",
                        "O-",
                        "AB+",
                        "AB-",
                    ]

                    b_val = (
                        editing_p.get("blood_group")
                        if editing_p.get("blood_group") in blood_options
                        else "Chưa xác định"
                    )

                    b_idx = blood_options.index(b_val)

                    e_blood = st.selectbox("Nhóm máu", blood_options, index=b_idx)

                    allergies_str = (
                        ", ".join(editing_p.get("allergies", []))
                        if editing_p.get("allergies")
                        else ""
                    )

                    e_allergies = st.text_input(
                        "Dị ứng (cách nhau bởi dấu phẩy)", value=allergies_str
                    )

                    e_address = st.text_input(
                        "Địa chỉ thường trú", value=editing_p.get("address", "")
                    )

                st.divider()

                submitted_update = st.form_submit_button(
                    "Lưu thay đổi", type="primary", use_container_width=True
                )

                if submitted_update:

                    cleaned_e_name = raw_e_name.strip()
                    e_phone_body = e_phone_suffix.strip()

                    if e_phone_body.startswith("0"):
                        e_phone_body = e_phone_body[1:]

                    vietnamese_name_regex = (
                        r"^[a-zA-Zàáảãạăằắẳẵặâầấẩẫậ"
                        r"èéẻẽẹêềếểễệìíỉĩịòóỏõọ"
                        r"ôồốổỗộơờớởỡợùúủũụưừứ"
                        r"ửữựỳýỷỹỵĐđ\s]+$"
                    )

                    if not e_code or not cleaned_e_name:
                        st.error("Vui lòng điền đầy đủ " "Mã bệnh nhân và Họ tên.")

                    elif not re.match(vietnamese_name_regex, cleaned_e_name):
                        st.error("Họ và tên chỉ được chứa chữ cái!")

                    elif not e_phone_body.isdigit() or not (
                        9 <= len(e_phone_body) <= 10
                    ):
                        st.error("Số điện thoại không hợp lệ!")

                    else:
                        full_e_phone = f"+84{e_phone_body}"
                        formatted_e_name = cleaned_e_name.title()

                        allergies_list = (
                            [a.strip() for a in e_allergies.split(",") if a.strip()]
                            if e_allergies
                            else []
                        )

                        update_data = {
                            "patient_code": e_code,
                            "full_name": formatted_e_name,
                            "dob": str(e_dob),
                            "gender": e_gender,
                            "phone": full_e_phone,
                            "address": e_address,
                            "blood_group": (
                                e_blood if e_blood != "Chưa xác định" else None
                            ),
                            "allergies": allergies_list,
                        }

                        try:
                            res, status_code = api_update_patient(
                                chosen_id_edit, update_data
                            )

                            if status_code == 200:
                                st.toast("Cập nhật thông tin " "bệnh nhân thành công!")

                                st.success(
                                    "Cập nhật thông tin " "bệnh nhân thành công!"
                                )

                                st.rerun()

                            else:
                                st.error(f"Lỗi từ API: {res}")

                        except Exception as e:
                            st.error(f"Lỗi kết nối API: {e}")

    else:
        st.warning("Không tìm thấy bệnh nhân phù hợp " "để chỉnh sửa.")


# ============================================================
# TAB 4 - XÓA BỆNH NHÂN
# Giữ nguyên API và hành vi xóa hiện tại
# ============================================================

with tab_delete:

    render_html("""
    <div class="patient-section">
        <div class="patient-section-title">
            Xóa hồ sơ bệnh nhân
        </div>
        <div class="patient-section-desc">
            Tìm kiếm bệnh nhân và xác nhận thao tác xóa.
        </div>
    </div>
    """)

    render_html("""
    <div class="patient-note">
        Lưu ý: Việc xóa bệnh nhân có thể đồng thời
        xóa toàn bộ hồ sơ bệnh án liên quan,
        theo chức năng hiện tại của hệ thống.
    </div>
    """)

    search_del = st.text_input(
        "Tìm kiếm bệnh nhân cần xóa (Họ tên, Mã BN, SĐT)",
        placeholder="Nhập thông tin bệnh nhân cần xóa...",
        key="search_del_tab",
    )

    patients_del, _ = api_get_patients(
        skip=0, limit=1000, search=search_del if search_del else None
    )

    if patients_del:

        patient_options_del = {
            (
                f"{p.get('patient_code')} - "
                f"{p.get('full_name')} "
                f"({p.get('phone', 'Không có SĐT')})"
            ): str(p.get("_id") or p.get("id"))
            for p in patients_del
        }

        selected_label_del = st.selectbox(
            "Chọn bệnh nhân từ kết quả tìm kiếm",
            options=list(patient_options_del.keys()),
            key="select_del_tab",
        )

        chosen_id_del = (
            patient_options_del[selected_label_del] if selected_label_del else None
        )

        target_p = next(
            (
                p
                for p in patients_del
                if str(p.get("_id") or p.get("id")) == chosen_id_del
            ),
            None,
        )

        if target_p:

            render_html(f"""
            <div class="patient-section">
                <div class="patient-danger-title">
                    Xác nhận xóa hồ sơ
                </div>
                <div class="patient-danger-note">
                    Bệnh nhân:
                    <b>{escape(str(target_p.get("full_name", "")))}</b>
                    <br>
                    Mã bệnh nhân:
                    <b>{escape(str(target_p.get("patient_code", "")))}</b>
                </div>
            </div>
            """)

            st.warning(
                "Cảnh báo: Thao tác này sẽ xóa vĩnh viễn "
                f"bệnh nhân **{target_p.get('full_name')}** "
                f"({target_p.get('patient_code')}) "
                "**ĐỒNG THỜI XÓA TOÀN BỘ HỒ SƠ BỆNH ÁN** "
                "liên quan!"
            )

            if st.button(
                "Xác nhận xóa bệnh nhân và toàn bộ bệnh án",
                type="primary",
                use_container_width=True,
            ):

                try:
                    status_code = api_delete_patient(chosen_id_del)

                    if status_code in [200, 204]:
                        st.toast(
                            "Đã xóa vĩnh viễn bệnh nhân "
                            "và các hồ sơ bệnh án liên quan!"
                        )

                        st.success(
                            "Đã xóa thành công bệnh nhân "
                            "và toàn bộ hồ sơ bệnh án liên quan!"
                        )

                        st.rerun()

                    else:
                        st.error(
                            "Lỗi khi xóa bệnh nhân qua API, " f"mã lỗi: {status_code}"
                        )

                except Exception as e:
                    st.error("Lỗi kết nối API khi thực hiện xóa: " f"{e}")

    else:
        st.warning("Không tìm thấy bệnh nhân phù hợp để xóa.")


# ============================================================
# 8. FOOTER
# ============================================================

render_html("""
<div class="patient-footer">
    MediSpace · Hệ thống quản lý hồ sơ bệnh án điện tử
    <br>
    Quản lý bệnh nhân · MongoDB Document Store
</div>
""")
