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
    api_get_revisit_rate
)

st.set_page_config(page_title="Thống Kê Y Tế | MediSpace", page_icon="📊", layout="wide")

st.title("📊 Báo Cáo Thống Kê Y Tế & Aggregation Pipelines")
st.caption("Dữ liệu lấy qua FastAPI Analytics API; tính toán bằng MongoDB Aggregation Framework ($match, $group, $lookup, $switch, $facet)")

# Nút kích hoạt báo cáo (Theo đúng kịch bản bảo vệ của SV2)
col_btn, col_empty = st.columns([1, 2])
with col_btn:
    btn_run = st.button("🚀 KÍCH HOẠT BÁO CÁO THỐNG KÊ DỊCH TỄ / BỆNH LÝ", type="primary", width="stretch")

if not btn_run and "reports_active" not in st.session_state:
    st.info("👉 Nhấn vào nút phía trên để gọi API thống kê và chạy Aggregation Pipelines trên MongoDB.")
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
st.subheader("1. Thống Kê Số Lượng Ca Khám Theo Chuyên Khoa")

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
            color_discrete_map={"TIM_MACH": "#EF553B", "DA_LIEU": "#00CC96", "RANG_HAM_MAT": "#636EFA"}
        )
        st.plotly_chart(fig_pie, width="stretch")
    with c2:
        fig_bar = px.bar(
            df_dept, 
            x="department", 
            y=["total_visits", "follow_up_count"], 
            barmode="group",
            title="Tổng ca khám và số ca cần tái khám",
            labels={"value": "Số lượng ca", "department": "Chuyên khoa", "variable": "Chỉ số"}
        )
        st.plotly_chart(fig_bar, width="stretch")

    with st.expander("🔍 Xem câu lệnh MongoDB Aggregation Pipeline (Pipeline 1)"):
        st.code("""
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
        """, language="javascript")
else:
    st.warning("Chưa có dữ liệu bệnh án.")

st.markdown("---")

# 2. Thống kê theo nhóm tuổi
st.subheader("2. Phân Bổ Ca Bệnh Theo Nhóm Tuổi Bệnh Nhân")

if age_stats:
    df_age = pd.DataFrame(age_stats)
    fig_age = px.bar(
        df_age,
        x="age_group",
        y="count",
        color="department",
        title="Số ca khám theo nhóm tuổi và chuyên khoa ($lookup & $switch)",
        barmode="stack"
    )
    st.plotly_chart(fig_age, width="stretch")
    
    with st.expander("🔍 Xem câu lệnh MongoDB Aggregation Pipeline (Pipeline 2)"):
        st.code("""
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
        """, language="javascript")

st.markdown("---")

# 3. Thống kê tần suất và tỷ lệ tái khám
st.subheader("3. Thống Kê Tần Suất & Tỷ Lệ Bệnh Nhân Tái Khám")

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Tổng bệnh nhân từng khám", f"{revisit_data.get('total_unique_patients', 0)} người")
with m2:
    st.metric("Bệnh nhân tái khám (>= 2 lần)", f"{revisit_data.get('revisit_patients', 0)} người")
with m3:
    st.metric("Bệnh nhân khám 1 lần", f"{revisit_data.get('single_visit_patients', 0)} người")
with m4:
    st.metric("Tỷ Lệ Tái Khám Chung", f"{revisit_data.get('revisit_rate_percent', 0.0)} %")

with st.expander("🔍 Xem câu lệnh MongoDB Aggregation Pipeline (Pipeline 3 với $facet)"):
    st.code("""
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
    """, language="javascript")
