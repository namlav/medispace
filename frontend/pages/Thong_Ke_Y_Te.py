import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

from frontend.api_client import (
    api_get_department_stats,
    api_get_age_groups,
    api_get_revisit_rate,
)

st.set_page_config(page_title="Thống kê y tế | MediSpace", layout="wide")

# ============================================================
# MEDISPACE - HEALTHCARE ANALYTICS UI
# Chỉ thay đổi giao diện, không thay đổi API hay xử lý
# ============================================================

st.markdown(
    """
<style>
:root {
    --analytics-primary: #167D70;
    --analytics-primary-dark: #10665B;
    --analytics-soft: #E8F5F2;
    --analytics-bg: #F5F8FA;
    --analytics-heading: #203B49;
    --analytics-text: #526672;
    --analytics-muted: #80909A;
    --analytics-border: #E1E9ED;
}

/* Giao diện tổng thể */
.stApp {
    background-color: var(--analytics-bg);
}

.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

/* Header */
.ms-analytics-header {
    position: relative;
    padding: 35px 38px;
    margin-bottom: 26px;
    border: 1px solid #DCEBE7;
    border-radius: 18px;
    background: linear-gradient(
        115deg,
        #FFFFFF 0%,
        #E8F5F2 100%
    );
    overflow: hidden;
}

.ms-analytics-header::after {
    content: "";
    position: absolute;
    width: 190px;
    height: 190px;
    border-radius: 50%;
    top: -95px;
    right: -40px;
    background: rgba(22,125,112,0.06);
    pointer-events: none;
}

.ms-analytics-eyebrow {
    color: #167D70;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.5px;
    margin-bottom: 12px;
}

.ms-analytics-title {
    color: #203B49;
    font-size: clamp(28px,3vw,38px);
    font-weight: 750;
    line-height: 1.3;
    margin: 0 0 12px 0;
}

.ms-analytics-description {
    color: #526672;
    font-size: 14px;
    line-height: 1.8;
    max-width: 800px;
    margin: 0;
}

.ms-analytics-tags {
    display: flex;
    gap: 9px;
    flex-wrap: wrap;
    margin-top: 20px;
}

.ms-analytics-tag {
    display: inline-block;
    padding: 7px 12px;
    background: #FFFFFF;
    border: 1px solid #DCEBE7;
    border-radius: 20px;
    color: #167D70;
    font-size: 12px;
    font-weight: 600;
}

/* Thanh kích hoạt báo cáo */
.ms-analytics-activation {
    background: #FFFFFF;
    border: 1px solid #E1E9ED;
    border-radius: 14px;
    padding: 19px 24px;
    margin: 10px 0 16px;
}

.ms-analytics-activation-title {
    color: #203B49;
    font-size: 17px;
    font-weight: 700;
    margin-bottom: 6px;
}

.ms-analytics-activation-desc {
    color: #80909A;
    font-size: 13px;
    line-height: 1.7;
}

/* Tiêu đề mỗi phần thống kê */
.ms-analytics-section {
    padding: 15px 0 9px;
    margin-top: 16px;
}

.ms-analytics-section-number {
    display: inline-block;
    color: #167D70;
    background: #E8F5F2;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 12px;
}

.ms-analytics-section-title {
    font-size: 21px;
    font-weight: 700;
    color: #203B49;
    margin-bottom: 7px;
}

.ms-analytics-section-desc {
    font-size: 13px;
    color: #80909A;
    line-height: 1.8;
}

/* Nút kích hoạt */
.stButton > button {
    border-radius: 9px;
    min-height: 45px;
    font-size: 13px;
    font-weight: 600;
    transition: background-color 0.2s ease;
}

.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background: #167D70;
    color: #FFFFFF;
    border-color: #167D70;
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background: #10665B;
    color: #FFFFFF;
    border-color: #10665B;
}

/* Biểu đồ Plotly */
[data-testid="stPlotlyChart"] {
    background: #FFFFFF;
    border: 1px solid #E1E9ED;
    border-radius: 15px;
    padding: 14px 10px;
    overflow: hidden;
}

/* Expander hiển thị Aggregation Pipeline */
[data-testid="stExpander"] {
    background: #FFFFFF;
    border: 1px solid #E1E9ED;
    border-radius: 12px;
    overflow: hidden;
    margin: 14px 0 19px;
}

[data-testid="stExpander"] summary {
    font-weight: 600;
    color: #203B49;
}

/* Thẻ chỉ số tái khám */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E1E9ED;
    border-radius: 14px;
    padding: 22px 19px;
    min-height: 140px;
    box-shadow: 0 4px 18px rgba(32,59,73,0.035);
}

[data-testid="stMetricLabel"] {
    color: #526672;
    font-size: 13px;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: #167D70;
    font-size: clamp(19px,2vw,27px);
    font-weight: 750;
}

/* Thông báo */
[data-testid="stAlert"] {
    border-radius: 11px;
}

/* Vùng câu lệnh */
[data-testid="stCode"] {
    border-radius: 10px;
    overflow: hidden;
}

/* Đường phân cách */
hr {
    border-color: #E1E9ED;
    opacity: 0.8;
    margin: 26px 0;
}

/* Footer */
.ms-analytics-footer {
    text-align: center;
    border-top: 1px solid #E1E9ED;
    padding-top: 20px;
    margin-top: 38px;
    color: #80909A;
    font-size: 12px;
}

@media (max-width: 768px) {
    .ms-analytics-header {
        padding: 24px;
    }

    [data-testid="stMetric"] {
        min-height: 105px;
        padding: 15px;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


def analytics_html(html):
    cleaned = "\n".join(line.lstrip() for line in html.splitlines()).strip()

    st.markdown(cleaned, unsafe_allow_html=True)


def analytics_section(number, title, description):
    analytics_html(f"""
    <div class="ms-analytics-section">
        <div class="ms-analytics-section-number">
            {number}
        </div>
        <div class="ms-analytics-section-title">
            {title}
        </div>
        <div class="ms-analytics-section-desc">
            {description}
        </div>
    </div>
    """)


# ============================================================
# HEADER - THỐNG KÊ Y TẾ
# ============================================================

analytics_html("""
<div class="ms-analytics-header">
    <div class="ms-analytics-eyebrow">
        MEDISPACE · HEALTHCARE ANALYTICS
    </div>

    <h1 class="ms-analytics-title">
        Thống kê y tế
    </h1>

    <p class="ms-analytics-description">
        Phân tích số lượng ca khám theo chuyên khoa,
        phân bố nhóm tuổi và tần suất tái khám.
        Dữ liệu được xử lý bằng MongoDB Aggregation
        Framework thông qua FastAPI.
    </p>

    <div class="ms-analytics-tags">
        <span class="ms-analytics-tag">
            MongoDB Aggregation
        </span>
        <span class="ms-analytics-tag">
            Analytics API
        </span>
        <span class="ms-analytics-tag">
            Plotly Visualization
        </span>
    </div>
</div>
""")


# ============================================================
# KHU VỰC KÍCH HOẠT BÁO CÁO
# ============================================================

analytics_html("""
<div class="ms-analytics-activation">
    <div class="ms-analytics-activation-title">
        Báo cáo thống kê dịch tễ và bệnh lý
    </div>
    <div class="ms-analytics-activation-desc">
        Kích hoạt truy vấn thống kê để phân tích
        dữ liệu y tế hiện có trong hệ thống.
    </div>
</div>
""")

col_btn, col_empty = st.columns([1, 2])

with col_btn:
    btn_run = st.button("Kích hoạt báo cáo thống kê", type="primary", width="stretch")

if not btn_run and "reports_active" not in st.session_state:
    st.info(
        "Nhấn vào nút phía trên để gọi API thống kê và chạy Aggregation Pipelines trên MongoDB."
    )
    st.stop()

st.session_state["reports_active"] = True

try:
    dept_stats = api_get_department_stats()
    age_stats = api_get_age_groups()
    revisit_data = api_get_revisit_rate()
except Exception as e:
    st.error(f"Không gọi được API thống kê: {e}")
    st.stop()

# 1. Thống kê theo chuyên khoa
analytics_section(
    "01 · CHUYÊN KHOA",
    "Thống kê số lượng ca khám theo chuyên khoa",
    "Phân tích tỷ lệ phân bổ ca khám và số ca cần tái khám giữa ba chuyên khoa.",
)

if dept_stats:
    df_dept = pd.DataFrame(dept_stats)
    c1, c2 = st.columns(2)
    with c1:
        fig_pie = px.pie(
            df_dept,
            names="department",
            values="total_visits",
            title="Tỷ lệ phân bổ ca bệnh theo chuyên khoa",
            color="department",
            color_discrete_map={
                "TIM_MACH": "#167D70",
                "DA_LIEU": "#55B9AE",
                "RANG_HAM_MAT": "#8FA8C9",
            },
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#203B49", size=12),
            title_font=dict(size=16, color="#203B49"),
            margin=dict(l=15, r=15, t=65, b=20),
            legend_title_text="Chuyên khoa",
        )
        st.plotly_chart(fig_pie, width="stretch")
    with c2:
        fig_bar = px.bar(
            df_dept,
            x="department",
            y=["total_visits", "follow_up_count"],
            barmode="group",
            title="Tổng ca khám và số ca cần tái khám",
            labels={
                "value": "Số lượng ca",
                "department": "Chuyên khoa",
                "variable": "Chỉ số",
            },
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#203B49", size=12),
            title_font=dict(size=16, color="#203B49"),
            margin=dict(l=15, r=15, t=65, b=30),
            colorway=["#167D70", "#8FA8C9"],
            legend=dict(orientation="h", y=-0.2),
        )
        fig_bar.update_yaxes(showgrid=True, gridcolor="#EDF2F4", zeroline=False)
        fig_bar.update_xaxes(showline=False)
        st.plotly_chart(fig_bar, width="stretch")

    with st.expander("🔍 Xem câu lệnh MongoDB Aggregation Pipeline (Pipeline 1)"):
        st.code(
            """
db.medical_records.aggregate([
  // $match: { visit_date: { $gte: ISODate("..."), $lte: ISODate("...") } }, // tùy chọn
  {
    $group: {
      _id: "$department",
      total_cases: { $sum: 1 },
      revisit_cases: { $sum: { $cond: [{ $eq: ["$follow_up_required", true] }, 1, 0] } },
      total_prescriptions: { $sum: { $size: { $ifNull: ["$prescriptions", []] } } },
      unique_doctors: { $addToSet: "$doctor_name" }
    }
  },
  {
    $project: {
      _id: 0,
      department: "$_id",
      total_cases: 1,
      revisit_cases: 1,
      total_prescriptions: 1,
      doctor_count: { $size: "$unique_doctors" },
      total_visits: "$total_cases",
      follow_up_count: "$revisit_cases"
    }
  },
  { $sort: { total_cases: -1 } }
])
        """,
            language="javascript",
        )
else:
    st.warning("Chưa có dữ liệu bệnh án.")

st.markdown("---")

# 2. Thống kê theo nhóm tuổi
analytics_section(
    "02 · NHÓM TUỔI",
    "Phân bổ ca bệnh theo nhóm tuổi bệnh nhân",
    "So sánh số lượng ca khám giữa các nhóm tuổi theo từng chuyên khoa.",
)
if age_stats:
    df_age = pd.DataFrame(age_stats)
    fig_age = px.bar(
        df_age,
        x="age_group",
        y="count",
        color="department",
        title="Số ca khám theo nhóm tuổi và chuyên khoa ($lookup & $switch)",
        barmode="stack",
    )
    fig_age.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#203B49", size=12),
        title_font=dict(size=16, color="#203B49"),
        margin=dict(l=20, r=20, t=65, b=35),
        legend=dict(orientation="h", y=-0.2, title_text="Chuyên khoa"),
        colorway=["#167D70", "#55B9AE", "#8FA8C9"],
    )
    fig_age.update_yaxes(showgrid=True, gridcolor="#EDF2F4", zeroline=False)
    st.plotly_chart(fig_age, width="stretch")

    with st.expander("Xem câu lệnh MongoDB Aggregation Pipeline (Pipeline 2)"):
        st.code(
            """
db.medical_records.aggregate([
  {
    $addFields: {
      patient_obj_id: {
        $convert: { input: "$patient_id", to: "objectId", onError: null, onNull: null }
      }
    }
  },
  {
    $lookup: {
      from: "patients",
      localField: "patient_obj_id",
      foreignField: "_id",
      as: "patient_info"
    }
  },
  { $unwind: "$patient_info" },
  {
    $addFields: {
      birth_date: {
        $dateFromString: {
          dateString: "$patient_info.dob",
          onError: null,
          onNull: null
        }
      }
    }
  },
  {
    $addFields: {
      age: { $dateDiff: { startDate: "$birth_date", endDate: "$visit_date", unit: "year" } }
    }
  },
  { $match: { age: { $gte: 0 } } },
  {
    $addFields: {
      age_group: {
        $switch: {
          branches: [
            { case: { $lte: ["$age", 18] }, then: "0-18" },
            { case: { $lte: ["$age", 40] }, then: "19-40" },
            { case: { $lte: ["$age", 60] }, then: "41-60" }
          ],
          default: "60+"
        }
      }
    }
  },
  {
    $group: {
      _id: { age_group: "$age_group", department: "$department" },
      count: { $sum: 1 }
    }
  },
  {
    $setWindowFields: {
      partitionBy: "$_id.age_group",
      output: { age_group_total: { $sum: "$count" } }
    }
  },
  {
    $project: {
      _id: 0,
      age_group: "$_id.age_group",
      department: "$_id.department",
      count: 1,
      percentage: {
        $round: [{ $multiply: [{ $divide: ["$count", "$age_group_total"] }, 100] }, 2]
      }
    }
  },
  { $sort: { age_group: 1, count: -1 } }
])
        """,
            language="javascript",
        )

st.markdown("---")

# 3. Thống kê tần suất và tỷ lệ tái khám
analytics_section(
    "03 · TÁI KHÁM",
    "Thống kê tần suất và tỷ lệ tái khám",
    "Tổng hợp số bệnh nhân đã khám, số bệnh nhân tái khám và tỷ lệ tái khám chung.",
)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(
        "Tổng bệnh nhân từng khám",
        f"{revisit_data.get('total_unique_patients', 0)} người",
    )
with m2:
    st.metric(
        "Bệnh nhân tái khám (>= 2 lần)",
        f"{revisit_data.get('revisit_patients', 0)} người",
    )
with m3:
    st.metric(
        "Bệnh nhân khám 1 lần", f"{revisit_data.get('single_visit_patients', 0)} người"
    )
with m4:
    st.metric(
        "Tỷ Lệ Tái Khám Chung", f"{revisit_data.get('revisit_rate_percent', 0.0)} %"
    )

with st.expander("Xem câu lệnh MongoDB Aggregation Pipeline (Pipeline 3 với $facet)"):
    st.code(
        """
db.medical_records.aggregate([
  {
    $group: {
      _id: "$patient_id",
      visit_count: { $sum: 1 },
      departments: { $addToSet: "$department" },
      latest_visit: { $max: "$visit_date" }
    }
  },
  {
    $facet: {
      summary: [
        {
          $group: {
            _id: null,
            total_unique_patients: { $sum: 1 },
            revisit_patients: { $sum: { $cond: [{ $gt: ["$visit_count", 1] }, 1, 0] } },
            single_visit_patients: { $sum: { $cond: [{ $eq: ["$visit_count", 1] }, 1, 0] } },
            total_visits: { $sum: "$visit_count" }
          }
        }
      ],
      distribution: [
        {
          $bucket: {
            groupBy: "$visit_count",
            boundaries: [1, 2, 4],
            default: ">3",
            output: { patient_count: { $sum: 1 } }
          }
        },
        {
          $project: {
            _id: 0,
            level: {
              $switch: {
                branches: [
                  { case: { $eq: ["$_id", 1] }, then: "1 lần" },
                  { case: { $eq: ["$_id", 2] }, then: "2-3 lần" }
                ],
                default: ">3 lần"
              }
            },
            patient_count: 1
          }
        }
      ],
      top_patients: [
        { $sort: { visit_count: -1 } },
        { $limit: 5 },
        {
          $project: {
            _id: 0,
            patient_id: "$_id",
            visit_count: 1,
            departments: 1,
            latest_visit: 1
          }
        }
      ]
    }
  },
  {
    $addFields: {
      total_unique_patients: { $ifNull: [{ $arrayElemAt: ["$summary.total_unique_patients", 0] }, 0] },
      revisit_patients: { $ifNull: [{ $arrayElemAt: ["$summary.revisit_patients", 0] }, 0] },
      single_visit_patients: { $ifNull: [{ $arrayElemAt: ["$summary.single_visit_patients", 0] }, 0] }
    }
  },
  {
    $project: {
      _id: 0,
      total_unique_patients: 1,
      revisit_patients: 1,
      single_visit_patients: 1,
      revisit_rate_percent: {
        $cond: [
          { $gt: ["$total_unique_patients", 0] },
          {
            $round: [
              { $multiply: [{ $divide: ["$revisit_patients", "$total_unique_patients"] }, 100] },
              2
            ]
          },
          0.0
        ]
      },
      distribution: 1,
      top_revisit_patients: "$top_patients"
    }
  }
])
    """,
        language="javascript",
    )
analytics_html("""
<div class="ms-analytics-footer">
    MediSpace · Hệ thống quản lý hồ sơ bệnh án điện tử
    <br>
    Thống kê y tế · MongoDB Aggregation Framework
</div>
""")
