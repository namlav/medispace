import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

from backend.app.services.analytics_service import AnalyticsService

st.set_page_config(page_title="Thống Kê Y Tế | MediSpace", page_icon="📊", layout="wide")

st.title("📊 Báo Cáo Thống Kê Y Tế & Aggregation Pipelines")
st.caption("Khai thác sức mạnh tính toán của MongoDB Aggregation Framework ($match, $group, $lookup, $switch, $facet)")

# Nút kích hoạt báo cáo (Theo đúng kịch bản bảo vệ của SV2)
col_btn, col_empty = st.columns([1, 2])
with col_btn:
    btn_run = st.button("🚀 KÍCH HOẠT BÁO CÁO THỐNG KÊ DỊCH TỄ / BỆNH LÝ", type="primary", use_container_width=True)

if not btn_run and "reports_active" not in st.session_state:
    st.info("👉 Nhấn vào nút phía trên để kích hoạt Aggregation Pipelines truy vấn dữ liệu từ MongoDB.")
    st.stop()

st.session_state["reports_active"] = True

# 1. Thống kê theo chuyên khoa
st.subheader("1. Thống Kê Số Lượng Ca Khám Theo Chuyên Khoa")
dept_stats = AnalyticsService.get_department_stats()

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
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        fig_bar = px.bar(
            df_dept, 
            x="department", 
            y=["total_visits", "follow_up_count"], 
            barmode="group",
            title="Tổng ca khám và số ca cần tái khám",
            labels={"value": "Số lượng ca", "department": "Chuyên khoa", "variable": "Chỉ số"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with st.expander("🔍 Xem câu lệnh MongoDB Aggregation Pipeline (Pipeline 1)"):
        st.code("""
db.medical_records.aggregate([
  {
    $group: {
      _id: "$department",
      total_visits: { $sum: 1 },
      follow_up_count: { $sum: { $cond: [{ $eq: ["$follow_up_required", true] }, 1, 0] } },
      unique_doctors: { $addToSet: "$doctor_name" }
    }
  },
  {
    $project: {
      _id: 0,
      department: "$_id",
      total_visits: 1,
      follow_up_count: 1,
      doctor_count: { $size: "$unique_doctors" }
    }
  },
  { $sort: { total_visits: -1 } }
])
        """, language="javascript")
else:
    st.warning("Chưa có dữ liệu bệnh án.")

st.markdown("---")

# 2. Thống kê theo nhóm tuổi
st.subheader("2. Phân Bổ Ca Bệnh Theo Nhóm Tuổi Bệnh Nhân")
age_stats = AnalyticsService.get_age_group_distribution()

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
    st.plotly_chart(fig_age, use_container_width=True)
    
    with st.expander("🔍 Xem câu lệnh MongoDB Aggregation Pipeline (Pipeline 2)"):
        st.code("""
db.medical_records.aggregate([
  {
    $addFields: {
      patient_obj_id: { $convert: { input: "$patient_id", to: "objectId" } }
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
      birth_year: { $toInt: { $substrBytes: ["$patient_info.dob", 0, 4] } }
    }
  },
  {
    $addFields: {
      approx_age: { $subtract: [2026, "$birth_year"] }
    }
  },
  {
    $addFields: {
      age_group: {
        $switch: {
          branches: [
            { case: { $lt: ["$approx_age", 18] }, then: "Dưới 18 tuổi (Nhi)" },
            { case: { $and: [{ $gte: ["$approx_age", 18] }, { $lte: ["$approx_age", 40] }] }, then: "18 - 40 tuổi (Thanh niên)" },
            { case: { $and: [{ $gte: ["$approx_age", 41] }, { $lte: ["$approx_age", 60] }] }, then: "41 - 60 tuổi (Trung niên)" }
          ],
          default: "Trên 60 tuổi (Cao tuổi)"
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
  { $sort: { "age_group": 1, "count": -1 } }
])
        """, language="javascript")

st.markdown("---")

# 3. Thống kê tần suất và tỷ lệ tái khám
st.subheader("3. Thống Kê Tần Suất & Tỷ Lệ Bệnh Nhân Tái Khám")
revisit_data = AnalyticsService.get_revisit_statistics()

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
      departments: { $addToSet: "$department" }
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
            boundaries: [1, 2, 4, 6, 100],
            default: "Khác",
            output: { patient_count: { $sum: 1 } }
          }
        }
      ]
    }
  }
])
    """, language="javascript")
