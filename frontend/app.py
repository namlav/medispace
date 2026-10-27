import sys
from pathlib import Path
import textwrap
from html import escape

import streamlit as st

# ============================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from frontend.api_client import api_get_patients, api_get_records
from frontend.ui_utils import load_css

# ============================================================
# 2. CẤU HÌNH TRANG
# ============================================================

st.set_page_config(
    page_title="MediSpace | Tổng quan",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Giữ CSS hiện tại, thêm CSS riêng cho Dashboard
load_css("dashboard.css")


# ============================================================
# 3. GIAO DIỆN DASHBOARD
# Không thay đổi backend hoặc API
# ============================================================

st.markdown(
    """
    
    <style>
        
/* ============================================================
   MEDISPACE - VISUAL ENHANCEMENTS
   Ảnh hero, hiệu ứng nền và hover
   ============================================================ */

/* 1. HERO HEADER */
.ms-home-hero {
    position: relative;
    isolation: isolate;
    min-height: 280px;
    padding-right: 38%;
    background: linear-gradient(
        115deg,
        #FFFFFF 0%,
        #E8F5F2 55%,
        #D7EEE8 100%
    );
    background-size: 200% 200%;
    animation: msGradient 14s ease-in-out infinite;
    overflow: hidden;
}

/* Nội dung nằm trên nền */
.ms-home-hero > :not(.ms-home-illustration) {
    position: relative;
    z-index: 2;
}

/* Ảnh minh họa bên phải */
.ms-home-illustration {
    position: absolute;
    z-index: 1;
    width: 37%;
    max-width: 430px;
    right: 5px;
    top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
    user-select: none;
    filter: drop-shadow(
        0 12px 22px rgba(22, 125, 112, 0.08)
    );
    animation: msHeroFloat 6s ease-in-out infinite;
}

/* Giữ nội dung rõ ràng */
.ms-home-desc {
    max-width: 700px;
}

/* Hình nền tròn mờ */
.ms-home-hero::before {
    content: "";
    position: absolute;
    width: 260px;
    height: 260px;
    border-radius: 50%;
    background: radial-gradient(
        circle,
        rgba(85,185,174,0.22),
        rgba(85,185,174,0)
    );
    right: 6%;
    bottom: -130px;
    z-index: 0;
    animation: msGlow 9s ease-in-out infinite;
}

/* 2. HOVER THẺ THỐNG KÊ */
.ms-home-stat {
    transition:
        transform 0.28s ease,
        box-shadow 0.28s ease,
        border-color 0.28s ease;
    will-change: transform;
}

.ms-home-stat:hover {
    transform: translateY(-5px);
    border-color: #B7DED5;
    box-shadow:
        0 12px 28px rgba(22,125,112,0.10);
}

/* 3. HOVER THẺ TRUY CẬP NHANH */
.ms-home-guide {
    transition:
        transform 0.28s ease,
        box-shadow 0.28s ease,
        border-color 0.28s ease;
}

.ms-home-guide:hover {
    transform: translateY(-4px);
    border-color: #A8D8CD;
    box-shadow:
        0 10px 25px rgba(22,125,112,0.08);
}

/* 4. HOVER THẺ THÔNG TIN CÔNG NGHỆ */
.ms-home-info {
    transition:
        transform 0.28s ease,
        box-shadow 0.28s ease,
        border-color 0.28s ease;
}

.ms-home-info:hover {
    transform: translateY(-3px);
    border-color: #B7DED5;
    box-shadow:
        0 9px 23px rgba(22,125,112,0.07);
}

/* 5. NHÃN CÔNG NGHỆ */
.ms-home-tag {
    transition:
        background-color 0.25s ease,
        border-color 0.25s ease,
        color 0.25s ease;
}

.ms-home-tag:hover {
    background: #167D70;
    color: #FFFFFF;
    border-color: #167D70;
}

/* 6. HIỆU ỨNG NỀN */
@keyframes msGradient {
    0%, 100% {
        background-position: 0% 50%;
    }
    50% {
        background-position: 100% 50%;
    }
}

@keyframes msHeroFloat {
    0%, 100% {
        transform: translateY(-50%);
    }
    50% {
        transform: translateY(calc(-50% - 7px));
    }
}

@keyframes msGlow {
    0%, 100% {
        opacity: 0.45;
        transform: scale(1);
    }
    50% {
        opacity: 0.8;
        transform: scale(1.12);
    }
}

/* 7. RESPONSIVE */
@media (max-width: 900px) {
    .ms-home-hero {
        min-height: 0;
        padding-right: 34%;
    }

    .ms-home-illustration {
        width: 34%;
        opacity: 0.75;
    }
}

@media (max-width: 600px) {
    .ms-home-hero {
        padding: 26px 22px;
        padding-right: 22px;
    }

    .ms-home-illustration {
        display: none;
    }

    .ms-home-hero::before {
        right: -100px;
    }
}

/* 8. TÔN TRỌNG NGƯỜI DÙNG GIẢM CHUYỂN ĐỘNG */
@media (prefers-reduced-motion: reduce) {
    .ms-home-hero,
    .ms-home-illustration,
    .ms-home-hero::before {
        animation: none !important;
    }

    .ms-home-stat,
    .ms-home-guide,
    .ms-home-info,
    .ms-home-tag {
        transition: none !important;
    }
}
        /* Khung nội dung */
        .block-container {
            max-width: 1450px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        /* Hero */
        .ms-home-hero {
            position: relative;
            background: linear-gradient(
                115deg,
                #ffffff 0%,
                #e8f5f2 100%
            );
            border: 1px solid #dcebe7;
            border-radius: 18px;
            padding: 35px 38px;
            margin-bottom: 26px;
            overflow: hidden;
        }

        .ms-home-hero::after {
            content: "";
            position: absolute;
            width: 190px;
            height: 190px;
            border-radius: 50%;
            background: rgba(22, 125, 112, 0.06);
            top: -95px;
            right: -40px;
        }

        .ms-home-eyebrow {
            display: inline-block;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 1.5px;
            color: #167d70;
            margin-bottom: 12px;
        }

        .ms-home-title {
            font-size: clamp(28px, 3vw, 39px);
            line-height: 1.25;
            color: #203b49;
            font-weight: 750;
            margin: 0 0 12px 0;
        }

        .ms-home-desc {
            color: #526672;
            font-size: 15px;
            line-height: 1.75;
            max-width: 750px;
            margin: 0;
        }

        .ms-home-tags {
            display: flex;
            gap: 9px;
            flex-wrap: wrap;
            margin-top: 22px;
        }

        .ms-home-tag {
            padding: 7px 12px;
            border-radius: 20px;
            background: white;
            border: 1px solid #dcebe7;
            color: #167d70;
            font-size: 12px;
            font-weight: 600;
        }

        /* Tiêu đề khu vực */
        .ms-home-section {
            margin: 20px 0 15px;
        }

        .ms-home-section-title {
            font-size: 21px;
            font-weight: 700;
            color: #203b49;
            margin-bottom: 5px;
        }

        .ms-home-section-desc {
            font-size: 13px;
            color: #7b8c95;
        }

        /* Thẻ thống kê */
        .ms-home-stat {
            min-height: 172px;
            padding: 24px;
            background: #ffffff;
            border: 1px solid #e1e9ed;
            border-radius: 15px;
            box-shadow: 0 4px 18px rgba(32,59,73,0.035);
        }

        .ms-home-stat-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
        }

        .ms-home-stat-label {
            font-size: 14px;
            font-weight: 600;
            color: #526672;
        }

        .ms-home-stat-icon {
            height: 43px;
            min-width: 43px;
            border-radius: 12px;
            display: inline-flex;
            justify-content: center;
            align-items: center;
            background: #e8f5f2;
            font-size: 22px;
        }

        .ms-home-stat-value {
            font-size: 33px;
            font-weight: 750;
            color: #203b49;
            margin-top: 14px;
            line-height: 1.25;
        }

        .ms-home-stat-value.connected {
            color: #167d70;
            font-size: 23px;
        }

        .ms-home-stat-value.disconnected {
            color: #d97706;
            font-size: 23px;
        }

        .ms-home-stat-foot {
            font-size: 12px;
            color: #7b8c95;
            margin-top: 10px;
            line-height: 1.55;
        }

        /* Thẻ hướng dẫn */
        .ms-home-guide {
            background: #ffffff;
            border: 1px solid #e1e9ed;
            border-radius: 15px;
            padding: 23px;
            min-height: 174px;
            margin-bottom: 10px;
        }

        .ms-home-guide-number {
            display: inline-block;
            background: #e8f5f2;
            color: #167d70;
            padding: 6px 11px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 700;
            margin-bottom: 14px;
        }

        .ms-home-guide-title {
            color: #203b49;
            font-size: 17px;
            font-weight: 700;
            margin-bottom: 9px;
        }

        .ms-home-guide-desc {
            font-size: 13px;
            line-height: 1.8;
            color: #526672;
        }

        /* Thông tin đồ án */
        .ms-home-info {
            background: #ffffff;
            border: 1px solid #e1e9ed;
            border-radius: 15px;
            padding: 24px 27px;
            margin-top: 14px;
        }

        .ms-home-info-title {
            color: #203b49;
            font-size: 17px;
            font-weight: 700;
            margin-bottom: 12px;
        }

        .ms-home-info-text {
            color: #526672;
            font-size: 13px;
            line-height: 1.9;
        }

        /* Footer */
        .ms-home-footer {
            margin-top: 35px;
            padding-top: 20px;
            border-top: 1px solid #e1e9ed;
            font-size: 12px;
            text-align: center;
            color: #7b8c95;
        }

        /* Điều chỉnh nút điều hướng */
        .stButton > button,
        [data-testid="stPageLink"] a {
            border-radius: 9px;
        }

        @media (max-width: 768px) {
            .ms-home-hero {
                padding: 24px;
            }

            .ms-home-stat {
                min-height: 145px;
            }

            .ms-home-guide {
                min-height: 0;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# MEDISPACE DASHBOARD V2 - CSS BỔ SUNG
# Chỉ bổ sung giao diện, không ảnh hưởng nghiệp vụ
# ============================================================

st.markdown(
    """
<style>

/* 1. NÂNG CẤP HEADER */
.ms-home-hero {
    position: relative;
    isolation: isolate;
    min-height: 300px;
    padding: 38px 40% 38px 38px;
    background: linear-gradient(
        115deg,
        #FFFFFF 0%,
        #E8F5F2 55%,
        #D7EEE8 100%
    );
    background-size: 200% 200%;
    animation: msGradient 14s ease-in-out infinite;
    overflow: hidden;
}

.ms-home-hero > .ms-home-illustration {
    position: absolute;
    z-index: 1;
    width: 37%;
    max-width: 430px;
    right: 5px;
    top: 50%;
    transform: translateY(-50%);
    animation: msHeroFloat 6s ease-in-out infinite;
    pointer-events: none;
}

.ms-home-hero > .ms-home-eyebrow,
.ms-home-hero > .ms-home-title,
.ms-home-hero > .ms-home-desc,
.ms-home-hero > .ms-home-tags {
    position: relative;
    z-index: 3;
}

/* 2. HAI MINI FLOATING CARDS */
.ms-home-hero > .ms-home-float-card {
    position: absolute;
    z-index: 4;
    width: 140px;
    padding: 12px 15px;
    border-radius: 13px;
    background: rgba(255, 255, 255, 0.94);
    border: 1px solid #D5E8E4;
    box-shadow: 0 12px 28px rgba(22,125,112,0.13);
    backdrop-filter: blur(8px);
}

.ms-home-float-card-one {
    top: 22px;
    right: 29%;
    animation: msFloatOne 6s ease-in-out infinite;
}

.ms-home-float-card-two {
    bottom: 18px;
    right: 23%;
    animation: msFloatTwo 7s ease-in-out infinite;
}

.ms-home-float-label {
    font-size: 11px;
    font-weight: 700;
    color: #167D70;
}

.ms-home-float-value {
    font-size: 24px;
    font-weight: 750;
    color: #203B49;
    margin-top: 5px;
}

.ms-home-float-note {
    font-size: 10px;
    line-height: 1.5;
    color: #80909A;
    margin-top: 4px;
}

/* 3. BA THẺ THỐNG KÊ */
.ms-home-stat {
    position: relative;
    overflow: hidden;
    background: linear-gradient(
        180deg,
        #FFFFFF,
        #FBFDFD
    );
    transition:
        transform .3s ease,
        box-shadow .3s ease,
        border-color .3s ease;
}

.ms-home-stat::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 4px;
    background: linear-gradient(
        90deg,
        #167D70,
        #55B9AE
    );
}

.ms-home-stat::after {
    content: "";
    position: absolute;
    right: -35px;
    bottom: -35px;
    width: 110px;
    height: 110px;
    border-radius: 50%;
    background: rgba(22,125,112,0.045);
    pointer-events: none;
}

.ms-home-stat:hover {
    transform: translateY(-6px);
    border-color: #B7DED5;
    box-shadow: 0 14px 28px rgba(22,125,112,0.12);
}

.ms-home-stat:hover .ms-home-stat-value {
    color: #167D70;
}

/* 4. WATERMARK TRUY CẬP NHANH */
.ms-home-guide {
    position: relative;
    overflow: hidden;
    min-height: 185px;
    transition:
        transform .3s ease,
        box-shadow .3s ease,
        border-color .3s ease;
}

.ms-home-guide::before {
    content: attr(data-mark);
    position: absolute;
    right: 12px;
    bottom: 8px;
    font-size: 60px;
    font-weight: 800;
    letter-spacing: -2px;
    color: rgba(22,125,112,0.075);
    pointer-events: none;
}

.ms-home-guide::after {
    content: "";
    position: absolute;
    top: -25px;
    right: -25px;
    width: 100px;
    height: 100px;
    border-radius: 50%;
    background: rgba(85,185,174,0.075);
    pointer-events: none;
}

.ms-home-guide:hover {
    transform: translateY(-5px);
    border-color: #A8D8CD;
    box-shadow: 0 12px 28px rgba(22,125,112,0.09);
}

.ms-home-guide:hover .ms-home-guide-title {
    color: #167D70;
}

/* 5. WATERMARK THÔNG TIN HỆ THỐNG */
.ms-home-info {
    position: relative;
    overflow: hidden;
    transition:
        transform .3s ease,
        box-shadow .3s ease,
        border-color .3s ease;
}

.ms-home-info::before {
    content: attr(data-mark);
    position: absolute;
    top: 12px;
    right: 20px;
    font-size: 57px;
    font-weight: 800;
    color: rgba(22,125,112,0.065);
    pointer-events: none;
}

.ms-home-info::after {
    content: "";
    position: absolute;
    right: -40px;
    bottom: -40px;
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: rgba(85,185,174,0.08);
    pointer-events: none;
}

.ms-home-info:hover {
    transform: translateY(-4px);
    border-color: #B7DED5;
    box-shadow: 0 12px 26px rgba(22,125,112,0.09);
}

/* 6. ANIMATION */
@keyframes msFloatOne {
    0%, 100% {
        transform: translateY(0);
    }
    50% {
        transform: translateY(-7px);
    }
}

@keyframes msFloatTwo {
    0%, 100% {
        transform: translateY(0);
    }
    50% {
        transform: translateY(7px);
    }
}

/* 7. RESPONSIVE */
@media (max-width: 1050px) {
    .ms-home-hero {
        padding-right: 38%;
    }

    .ms-home-float-card {
        display: none;
    }
}

@media (max-width: 820px) {
    .ms-home-hero {
        min-height: 0;
        padding: 26px 24px;
    }

    .ms-home-illustration,
    .ms-home-float-card {
        display: none !important;
    }
}

@media (prefers-reduced-motion: reduce) {
    .ms-home-hero,
    .ms-home-illustration,
    .ms-home-hero::before,
    .ms-home-float-card {
        animation: none !important;
    }

    .ms-home-stat,
    .ms-home-guide,
    .ms-home-info {
        transition: none !important;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# 4. LẤY DỮ LIỆU TỪ BACKEND
# ============================================================

connected = False
total_patients = None
total_records = None
connection_error = ""

try:
    # Dùng API hiện có, chỉ lấy total
    _, total_patients = api_get_patients(skip=0, limit=1)

    _, total_records = api_get_records(skip=0, limit=1)

    connected = True

except Exception as e:
    connected = False
    connection_error = str(e)


def format_total(value):
    if value is None:
        return "—"

    try:
        return f"{int(value):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "—"


# ============================================================
# HÀM HIỂN THỊ HTML AN TOÀN VỚI STREAMLIT
# ============================================================


def render_html(html):
    # Xóa khoảng trắng đầu mỗi dòng HTML
    # để Streamlit không hiểu nhầm thành code block.
    cleaned_html = "\n".join(line.lstrip() for line in html.splitlines()).strip()

    st.markdown(cleaned_html, unsafe_allow_html=True)


# ============================================================
# HERO ILLUSTRATION - MEDISPACE
# Hình vector trang trí, không ảnh hưởng API
# ============================================================

import base64

hero_svg = """
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 500 340" fill="none">

    <defs>
        <linearGradient id="screen" x1="0" y1="0"
                        x2="1" y2="1">
            <stop stop-color="#FFFFFF"/>
            <stop offset="1" stop-color="#E8F5F2"/>
        </linearGradient>

        <linearGradient id="panel" x1="0" y1="0"
                        x2="1" y2="1">
            <stop stop-color="#167D70"/>
            <stop offset="1" stop-color="#55B9AE"/>
        </linearGradient>

        <filter id="shadow" x="-30%" y="-30%"
                width="160%" height="160%">
            <feDropShadow dx="0" dy="12"
                          stdDeviation="14"
                          flood-color="#167D70"
                          flood-opacity=".14"/>
        </filter>
    </defs>

    <!-- Hình nền trang trí -->
    <circle cx="250" cy="170" r="145"
            fill="#CDEBE5" opacity=".5"/>
    <circle cx="430" cy="65" r="24"
            fill="#B8DED6" opacity=".65"/>
    <circle cx="75" cy="260" r="16"
            fill="#B8DED6" opacity=".6"/>

    <!-- Màn hình -->
    <rect x="105" y="57" width="310" height="214"
          rx="19" fill="url(#screen)"
          stroke="#C9E2DD" stroke-width="2"
          filter="url(#shadow)"/>

    <!-- Thanh tiêu đề màn hình -->
    <path d="M105 77 Q105 57 125 57 H395
             Q415 57 415 77 V100 H105 Z"
          fill="#167D70"/>

    <circle cx="128" cy="79" r="5" fill="#B1E4D9"/>
    <circle cx="145" cy="79" r="5" fill="#B1E4D9"/>
    <circle cx="162" cy="79" r="5" fill="#B1E4D9"/>

    <rect x="290" y="73" width="93" height="12"
          rx="6" fill="#FFFFFF" opacity=".3"/>

    <!-- Menu bên trái -->
    <rect x="122" y="116" width="68" height="135"
          rx="9" fill="#E5F3F0"/>

    <rect x="132" y="130" width="48" height="9"
          rx="4" fill="#167D70" opacity=".7"/>
    <rect x="132" y="152" width="39" height="7"
          rx="3" fill="#9CCBC2"/>
    <rect x="132" y="172" width="46" height="7"
          rx="3" fill="#9CCBC2"/>
    <rect x="132" y="192" width="32" height="7"
          rx="3" fill="#9CCBC2"/>

    <!-- Card số liệu -->
    <rect x="204" y="116" width="88" height="57"
          rx="10" fill="#FFFFFF"
          stroke="#D8EAE6"/>

    <rect x="216" y="130" width="38" height="6"
          rx="3" fill="#AACEC7"/>
    <rect x="216" y="145" width="54" height="14"
          rx="5" fill="#167D70" opacity=".85"/>

    <rect x="303" y="116" width="95" height="57"
          rx="10" fill="#FFFFFF"
          stroke="#D8EAE6"/>

    <rect x="316" y="130" width="41" height="6"
          rx="3" fill="#AACEC7"/>
    <rect x="316" y="145" width="66" height="14"
          rx="5" fill="#55B9AE"/>

    <!-- Biểu đồ -->
    <rect x="204" y="183" width="194" height="68"
          rx="10" fill="#FFFFFF"
          stroke="#D8EAE6"/>

    <path d="M216 235 H385"
          stroke="#E0EAE7" stroke-width="1.5"/>

    <path d="M216 223 L244 212 L271 218
             L299 201 L326 210 L353 194
             L385 201"
          stroke="#167D70"
          stroke-width="4"
          stroke-linecap="round"
          stroke-linejoin="round"/>

    <path d="M216 223 L244 212 L271 218
             L299 201 L326 210 L353 194
             L385 201 V235 H216 Z"
          fill="#55B9AE" opacity=".12"/>

    <!-- Chân màn hình -->
    <rect x="244" y="271" width="36" height="25"
          fill="#9AC9C1"/>
    <rect x="218" y="293" width="90" height="10"
          rx="5" fill="#7BAEA5"/>

    <!-- Hồ sơ nổi -->
    <rect x="40" y="135" width="105" height="105"
          rx="14" fill="#FFFFFF"
          stroke="#D5E8E4"
          filter="url(#shadow)"/>

    <rect x="57" y="153" width="70" height="10"
          rx="5" fill="#167D70" opacity=".75"/>

    <rect x="57" y="176" width="58" height="6"
          rx="3" fill="#B1D5CE"/>

    <rect x="57" y="192" width="70" height="6"
          rx="3" fill="#B1D5CE"/>

    <rect x="57" y="208" width="43" height="6"
          rx="3" fill="#B1D5CE"/>

    <!-- Card nổi thứ hai -->
    <rect x="380" y="196" width="85" height="82"
          rx="13" fill="#FFFFFF"
          stroke="#D5E8E4"
          filter="url(#shadow)"/>

    <rect x="394" y="212" width="50" height="8"
          rx="4" fill="#167D70" opacity=".7"/>

    <rect x="394" y="230" width="57" height="7"
          rx="3" fill="#B1D5CE"/>

    <rect x="394" y="246" width="39" height="7"
          rx="3" fill="#B1D5CE"/>
</svg>
"""

hero_image_b64 = base64.b64encode(hero_svg.encode("utf-8")).decode("utf-8")

# ============================================================
# 5. HEADER - LỜI CHÀO
# ============================================================

render_html(f"""
    <div class="ms-home-hero">

        <div
            class="ms-home-illustration"
            style="background-image: url('data:image/svg+xml;base64,{hero_image_b64}');"
            aria-hidden="true">
        </div>

        <div class="ms-home-float-card ms-home-float-card-one">
            <div class="ms-home-float-label">
                Bệnh nhân
            </div>
            <div class="ms-home-float-value">
                {format_total(total_patients)}
            </div>
            <div class="ms-home-float-note">
                Hồ sơ đang quản lý
            </div>
        </div>

        <div class="ms-home-float-card ms-home-float-card-two">
            <div class="ms-home-float-label">
                Bệnh án
            </div>
            <div class="ms-home-float-value">
                {format_total(total_records)}
            </div>
            <div class="ms-home-float-note">
                Lượt khám đã lưu
            </div>
        </div>

        <div class="ms-home-eyebrow">
            MEDISPACE · MEDICAL MANAGEMENT
        </div>

        <h1 class="ms-home-title">
            Tổng quan hệ thống
        </h1>

        <p class="ms-home-desc">
            Chào mừng đến với MediSpace – Hệ thống quản lý
            hồ sơ bệnh án điện tử tại phòng khám.
            Quản lý thông tin bệnh nhân, lưu trữ bệnh án
            đa chuyên khoa và phân tích dữ liệu y tế
            trên nền tảng MongoDB.
        </p>

        <div class="ms-home-tags">
            <span class="ms-home-tag">MongoDB</span>
            <span class="ms-home-tag">FastAPI</span>
            <span class="ms-home-tag">Streamlit</span>
            <span class="ms-home-tag">Document Store</span>
        </div>
    </div>
    """)


# ============================================================
# 6. THỐNG KÊ TỔNG QUAN - 3 THẺ
# ============================================================

render_html("""
    <div class="ms-home-section">
        <div class="ms-home-section-title">
            Thống kê tổng quan
        </div>
        <div class="ms-home-section-desc">
            Dữ liệu được lấy trực tiếp từ hệ thống quản lý.
        </div>
    </div>
    """)

col1, col2, col3 = st.columns(3, gap="medium")

# THẺ 1 - BỆNH NHÂN
with col1:
    render_html(f"""
        <div class="ms-home-stat">
            <div class="ms-home-stat-top">
                <div class="ms-home-stat-label">
                    Tổng bệnh nhân
                </div>
                <div class="ms-home-stat-icon"></div>
            </div>

            <div class="ms-home-stat-value">
                {format_total(total_patients)}
            </div>

            <div class="ms-home-stat-foot">
                Hồ sơ bệnh nhân đang được quản lý
            </div>
        </div>
        """)

# THẺ 2 - BỆNH ÁN
with col2:
    render_html(f"""
        <div class="ms-home-stat">
            <div class="ms-home-stat-top">
                <div class="ms-home-stat-label">
                    Tổng bệnh án
                </div>
                <div class="ms-home-stat-icon"></div>
            </div>

            <div class="ms-home-stat-value">
                {format_total(total_records)}
            </div>

            <div class="ms-home-stat-foot">
                Tổng lượt khám được lưu trữ
            </div>
        </div>
        """)

# THẺ 3 - TRẠNG THÁI API
with col3:
    status_text = "Đang hoạt động" if connected else "Mất kết nối"

    status_class = "connected" if connected else "disconnected"

    status_note = (
        "API bệnh nhân và bệnh án phản hồi thành công"
        if connected
        else "Không thể lấy dữ liệu từ API"
    )

    render_html(f"""
        <div class="ms-home-stat">
            <div class="ms-home-stat-top">
                <div class="ms-home-stat-label">
                    Trạng thái kết nối
                </div>
                <div class="ms-home-stat-icon"></div>
            </div>

            <div class="ms-home-stat-value {status_class}">
                {status_text}
            </div>

            <div class="ms-home-stat-foot">
                {status_note}
            </div>
        </div>
        """)


# ============================================================
# 7. ĐIỀU KHIỂN VÀ TRẠNG THÁI
# ============================================================

col_refresh, col_message = st.columns([1, 3], vertical_alignment="center")

with col_refresh:
    if st.button("Làm mới dữ liệu", use_container_width=True):
        st.rerun()

with col_message:
    if connected:
        st.success("Đã tải dữ liệu thành công từ API.", icon="✅")
    else:
        st.warning("Không thể kết nối API. " "Hãy kiểm tra FastAPI Backend.", icon="⚠️")

if not connected:
    with st.expander("Xem chi tiết lỗi kết nối"):
        st.code(connection_error, language="text")


# ============================================================
# 8. HƯỚNG DẪN THAO TÁC NHANH
# ============================================================

render_html("""
    <div class="ms-home-section">
        <div class="ms-home-section-title">
            Truy cập nhanh
        </div>

        <div class="ms-home-section-desc">
            Lựa chọn khu vực để bắt đầu quản lý
            và khai thác dữ liệu bệnh án.
        </div>
    </div>
    """)

guide1, guide2, guide3 = st.columns(3, gap="medium")


# HƯỚNG DẪN 1
with guide1:
    render_html("""
    <div class="ms-home-guide guide-patient" data-mark="BN">
        <div class="ms-home-guide-number">01 · HỒ SƠ</div>
        <div class="ms-home-guide-title">
            Quản lý bệnh nhân
        </div>
        <div class="ms-home-guide-desc">
            Xem danh sách bệnh nhân, tìm kiếm hồ sơ,
            thêm bệnh nhân mới và cập nhật thông tin
            đang lưu trữ trong hệ thống.
        </div>
    </div>
    """)

    st.page_link(
        "pages/Benh_Nhan.py",
        label="Mở quản lý bệnh nhân",
        icon="➡️",
        use_container_width=True,
    )


# HƯỚNG DẪN 2
with guide2:
    render_html("""
    <div class="ms-home-guide guide-record" data-mark="BA">
        <div class="ms-home-guide-number">02 · KHÁM BỆNH</div>
        <div class="ms-home-guide-title">
            Khám bệnh động
        </div>
        <div class="ms-home-guide-desc">
            Lập bệnh án thuộc chuyên khoa Tim mạch,
            Da liễu hoặc Răng - Hàm - Mặt.
            Biểu mẫu thay đổi theo chuyên khoa.
        </div>
    </div>
    """)

    st.page_link(
        "pages/Kham_Benh_Dong.py",
        label="Mở khám bệnh động",
        icon="➡️",
        use_container_width=True,
    )


# HƯỚNG DẪN 3
with guide3:
    render_html("""
    <div class="ms-home-guide guide-analytics" data-mark="TK">
        <div class="ms-home-guide-number">03 · THỐNG KÊ</div>
        <div class="ms-home-guide-title">
            Thống kê y tế
        </div>
        <div class="ms-home-guide-desc">
            Phân tích số ca bệnh theo chuyên khoa,
            nhóm tuổi và tần suất tái khám
            bằng MongoDB Aggregation Pipeline.
        </div>
    </div>
    """)

    st.page_link(
        "pages/Thong_Ke_Y_Te.py",
        label="Mở thống kê y tế",
        icon="➡️",
        use_container_width=True,
    )


# ============================================================
# 9. THÔNG TIN HỆ THỐNG
# ============================================================

render_html("""
    <div class="ms-home-section">
        <div class="ms-home-section-title">
            Thông tin hệ thống
        </div>
        <div class="ms-home-section-desc">
            Kiến trúc và đặc điểm công nghệ của MediSpace.
        </div>
    </div>
    """)

info1, info2 = st.columns(2, gap="medium")

with info1:
    render_html("""
    <div class="ms-home-info info-db" data-mark="DB">
        <div class="ms-home-info-title">
            Cơ sở dữ liệu MongoDB
        </div>
        <div class="ms-home-info-text">
            Sử dụng mô hình Document Store để lưu trữ
            thông tin bệnh nhân và bệnh án điện tử.
            <br><br>
            Hỗ trợ dữ liệu chuyên khoa linh hoạt
            với các trường thông tin khác nhau
            trong cùng hệ thống.
        </div>
    </div>
    """)

with info2:
    render_html("""
    <div class="ms-home-info info-analytics" data-mark="PT">
        <div class="ms-home-info-title">
            Phân tích dữ liệu y tế
        </div>
        <div class="ms-home-info-text">
            Khai thác Aggregation Pipeline của MongoDB
            để thực hiện các báo cáo thống kê.
            <br><br>
            Theo dõi phân bố chuyên khoa, nhóm tuổi
            bệnh nhân và tần suất tái khám.
        </div>
    </div>
    """)


# ============================================================
# 10. FOOTER
# ============================================================

render_html("""
    <div class="ms-home-footer">
        MediSpace · Hệ thống quản lý hồ sơ bệnh án điện tử
        <br>
        Đồ án Cơ sở dữ liệu NoSQL · MongoDB Document Store
    </div>
    """)
