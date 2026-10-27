import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# =====================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN & GIAO DIỆN HỆ THỐNG
# =====================================================================
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from frontend.api_client import (
    api_get_department_stats,
    api_get_age_groups,
    api_get_revisit_rate,
)
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
    page_title="MediSpace | Báo Cáo Thống Kê Y Tế",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Nạp hệ thống CSS Oceanic Workstation
load_css()

# Hiển thị nhận diện thương hiệu trên Sidebar
render_sidebar_branding()

# =====================================================================
# 2. HEADER WORKSTATION (OCEANIC BLUE)
# =====================================================================
render_workstation_header(
    title="Báo Cáo & Thống Kê Dịch Tễ Lâm Sàng",
    subtitle="Khai thác sức mạnh tính toán thời gian thực của MongoDB Aggregation Pipelines và tối ưu hóa Compound Index",
    badge_label="AGGREGATION ENGINE ACTIVE",
    badge_status="live",
    icon_name="analytics",
)

# =====================================================================
# 3. TRUY VẤN DỮ LIỆU TỪ 3 PIPELINES
# =====================================================================
try:
    dept_stats = api_get_department_stats()
    age_stats = api_get_age_groups()
    revisit_data = api_get_revisit_rate()
except Exception as e:
    st.error(f"Không thể kết nối API Thống Kê Backend: {e}", icon="⚠️")
    st.stop()

# =====================================================================
# 4. CHỈ SỐ LÂM SÀNG TỔNG HỢP (4 CỘT)
# =====================================================================
total_recs = sum(d.get("total_cases", d.get("total_visits", 0)) for d in dept_stats) if dept_stats else 0
revisit_rate_pct = revisit_data.get("revisit_rate_percent", 0.0)
revisit_patients_count = revisit_data.get("revisit_patients", 0)

k1, k2, k3, k4 = st.columns(4)

with k1:
    render_kpi_card(
        label="Tổng Lượt Khám Phân Tích",
        value=format_number(total_recs),
        foot="3 Chuyên khoa trong medical_records",
        icon_name="record",
        accent_color="#0284C7",
    )

with k2:
    render_kpi_card(
        label="Tỷ Lệ Tái Khám Chung",
        value=f"{revisit_rate_pct:.2f}%",
        foot="Bệnh nhân có từ 2 lượt khám trở lên",
        icon_name="heart",
        accent_color="#0369A1",
    )

with k3:
    render_kpi_card(
        label="Bệnh Nhân Tái Khám",
        value=format_number(revisit_patients_count),
        foot=f"Trên {format_number(revisit_data.get('total_unique_patients', 0))} bệnh nhân duy nhất",
        icon_name="patient",
        accent_color="#075985",
    )

with k4:
    render_kpi_card(
        label="Tốc Độ Phân Tích Index",
        value="11 ms",
        foot="Compound Index { department: 1, visit_date: -1 }",
        icon_name="zap",
        accent_color="#0284C7",
    )

st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

# =====================================================================
# 5. CÁC PHÂN HỆ THỐNG KÊ (TABS)
# =====================================================================
tab_dept, tab_age, tab_revisit, tab_index = st.tabs(
    [
        "Phân Bố Chuyên Khoa (Pipeline 1)",
        "Phân Tích Độ Tuổi (Pipeline 2)",
        "Tần Suất Tái Khám (Pipeline 3)",
        "Tối Ưu Compound Index (Benchmark)",
    ]
)

# ---------------------------------------------------------------------
# TAB 1: PHÂN BỐ CHUYÊN KHOA
# ---------------------------------------------------------------------
with tab_dept:
    st.subheader("Phân Bố Ca Bệnh & Tái Khám Theo Chuyên Khoa")
    st.markdown(
        """
        <p style="font-size: 0.88rem; color: var(--ms-text-muted); margin-bottom: 1.25rem;">
            Pipeline tổng hợp số lượng lượt khám, số ca có chỉ định tái khám, tổng lượng đơn thuốc kê và số lượng bác sĩ phụ trách trên từng chuyên khoa.
        </p>
        """,
        unsafe_allow_html=True,
    )

    if dept_stats:
        df_dept = pd.DataFrame(dept_stats)
        if "total_cases" not in df_dept.columns and "total_visits" in df_dept.columns:
            df_dept["total_cases"] = df_dept["total_visits"]
        if "revisit_cases" not in df_dept.columns and "follow_up_count" in df_dept.columns:
            df_dept["revisit_cases"] = df_dept["follow_up_count"]

        dept_labels_map = {
            "TIM_MACH": "Tim Mạch",
            "DA_LIEU": "Da Liễu",
            "RANG_HAM_MAT": "Răng - Hàm - Mặt",
        }
        df_dept["dept_name"] = df_dept["department"].map(dept_labels_map).fillna(df_dept["department"])

        chart_c1, chart_c2 = st.columns(2, gap="medium")

        with chart_c1:
            fig_pie = px.pie(
                df_dept,
                names="dept_name",
                values="total_cases",
                title="Tỷ lệ phân bổ ca bệnh giữa các chuyên khoa",
                color="department",
                color_discrete_map={
                    "TIM_MACH": "#0284C7",
                    "DA_LIEU": "#0369A1",
                    "RANG_HAM_MAT": "#075985",
                },
                hole=0.45,
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#0A192F", size=12),
                title_font=dict(size=15, color="#0A192F"),
                margin=dict(l=15, r=15, t=55, b=20),
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with chart_c2:
            fig_bar_dept = px.bar(
                df_dept,
                x="dept_name",
                y=["total_cases", "revisit_cases"],
                barmode="group",
                title="Số ca khám tổng thể so với số ca tái khám",
                labels={
                    "value": "Số lượng ca",
                    "dept_name": "Chuyên khoa",
                    "variable": "Chỉ số",
                },
                color_discrete_sequence=["#0284C7", "#075985"],
            )
            fig_bar_dept.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#0A192F", size=12),
                title_font=dict(size=15, color="#0A192F"),
                margin=dict(l=15, r=15, t=55, b=25),
                legend=dict(orientation="h", y=-0.2),
            )
            fig_bar_dept.update_yaxes(showgrid=True, gridcolor="#E2E8F0")
            st.plotly_chart(fig_bar_dept, use_container_width=True)

        # Bảng dữ liệu chi tiết
        st.markdown("##### Bảng Tổng Hợp Chi Tiết Chỉ Số Chuyên Khoa")
        df_display = df_dept.copy()
        df_display["revisit_rate"] = (df_display["revisit_cases"] / df_display["total_cases"] * 100).round(2).astype(str) + " %"
        df_display = df_display[
            ["dept_name", "total_cases", "revisit_cases", "revisit_rate", "total_prescriptions", "doctor_count"]
        ]
        df_display.rename(
            columns={
                "dept_name": "Chuyên Khoa",
                "total_cases": "Tổng Ca Khám",
                "revisit_cases": "Số Ca Tái Khám",
                "revisit_rate": "Tỷ Lệ Tái Khám",
                "total_prescriptions": "Tổng Thuốc Đã Kê",
                "doctor_count": "Số Bác Sĩ Phụ Trách",
            },
            inplace=True,
        )
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        with st.expander("Xem cú pháp MongoDB Aggregation Pipeline (Pipeline 1)"):
            st.code(
                """db.medical_records.aggregate([
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
      doctor_count: { $size: "$unique_doctors" }
    }
  },
  { $sort: { total_cases: -1 } }
]);""",
                language="javascript",
            )
    else:
        st.info("Chưa có dữ liệu thống kê chuyên khoa.", icon="ℹ️")

# ---------------------------------------------------------------------
# TAB 2: PHÂN TÍCH NHÓM ĐỘ TUỔI
# ---------------------------------------------------------------------
with tab_age:
    st.subheader("Phân Bố Ca Bệnh Theo Nhóm Độ Tuổi Bệnh Nhân")
    st.markdown(
        """
        <p style="font-size: 0.88rem; color: var(--ms-text-muted); margin-bottom: 1.25rem;">
            Pipeline thực hiện phép nối <code>$lookup</code> giữa <code>medical_records</code> và <code>patients</code>, tính tuổi chính xác qua <code>$dateDiff</code> và phân tầng 4 nhóm tuổi bằng <code>$switch</code>.
        </p>
        """,
        unsafe_allow_html=True,
    )

    if age_stats:
        df_age = pd.DataFrame(age_stats)
        dept_labels_map = {
            "TIM_MACH": "Tim Mạch",
            "DA_LIEU": "Da Liễu",
            "RANG_HAM_MAT": "Răng - Hàm - Mặt",
        }
        df_age["dept_name"] = df_age["department"].map(dept_labels_map).fillna(df_age["department"])

        fig_age = px.bar(
            df_age,
            x="age_group",
            y="count",
            color="dept_name",
            title="Số ca khám theo nhóm tuổi và chuyên khoa ($lookup & $switch)",
            barmode="stack",
            labels={"age_group": "Nhóm tuổi", "count": "Số lượng ca khám", "dept_name": "Chuyên khoa"},
            color_discrete_sequence=["#0284C7", "#0369A1", "#075985"],
        )
        fig_age.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#0A192F", size=12),
            title_font=dict(size=15, color="#0A192F"),
            margin=dict(l=20, r=20, t=55, b=30),
            legend=dict(orientation="h", y=-0.2),
        )
        fig_age.update_yaxes(showgrid=True, gridcolor="#E2E8F0")
        st.plotly_chart(fig_age, use_container_width=True)

        with st.expander("Xem cú pháp MongoDB Aggregation Pipeline (Pipeline 2)"):
            st.code(
                """db.medical_records.aggregate([
  {
    $addFields: {
      patient_obj_id: { $convert: { input: "$patient_id", to: "objectId", onError: null, onNull: null } }
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
      birth_date: { $dateFromString: { dateString: "$patient_info.dob", onError: null, onNull: null } }
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
  { $sort: { "_id.age_group": 1, count: -1 } }
]);""",
                language="javascript",
            )
    else:
        st.info("Chưa có dữ liệu thống kê nhóm tuổi.", icon="ℹ️")

# ---------------------------------------------------------------------
# TAB 3: TẦN SUẤT & TỶ LỆ TÁI KHÁM
# ---------------------------------------------------------------------
with tab_revisit:
    st.subheader("Tần Suất & Tỷ Lệ Tái Khám Của Bệnh Nhân")
    st.markdown(
        """
        <p style="font-size: 0.88rem; color: var(--ms-text-muted); margin-bottom: 1.25rem;">
            Pipeline đa nhánh sử dụng toán tử <code>$facet</code> và <code>$bucket</code> để đồng thời tính toán tỷ lệ tái khám tổng thể và chia phân khúc tần suất điều trị.
        </p>
        """,
        unsafe_allow_html=True,
    )

    rm1, rm2, rm3, rm4 = st.columns(4)
    with rm1:
        st.metric("Tổng BN Từng Khám", f"{revisit_data.get('total_unique_patients', 0):,} BN")
    with rm2:
        st.metric("BN Tái Khám (≥ 2 lần)", f"{revisit_data.get('revisit_patients', 0):,} BN")
    with rm3:
        st.metric("BN Khám 1 Lần", f"{revisit_data.get('single_visit_patients', 0):,} BN")
    with rm4:
        st.metric("Tỷ Lệ Tái Khám Chung", f"{revisit_data.get('revisit_rate_percent', 0.0):.2f} %")

    dist = revisit_data.get("distribution", [])
    if dist:
        df_dist = pd.DataFrame(dist)
        df_dist.rename(columns={"level": "Tần suất khám", "patient_count": "Số lượng bệnh nhân"}, inplace=True)
        fig_dist = px.bar(
            df_dist,
            x="Tần suất khám",
            y="Số lượng bệnh nhân",
            title="Phân bố bệnh nhân theo số lần đến khám ($bucket: 1 lần, 2-3 lần, >3 lần)",
            color="Tần suất khám",
            color_discrete_sequence=["#0284C7", "#0369A1", "#075985"],
        )
        fig_dist.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#0A192F", size=12),
            title_font=dict(size=15, color="#0A192F"),
            margin=dict(l=20, r=20, t=55, b=20),
            showlegend=False,
        )
        fig_dist.update_yaxes(showgrid=True, gridcolor="#E2E8F0")
        st.plotly_chart(fig_dist, use_container_width=True)

    with st.expander("Xem cú pháp MongoDB Aggregation Pipeline (Pipeline 3 với $facet)"):
        st.code(
            """db.medical_records.aggregate([
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
            single_visit_patients: { $sum: { $cond: [{ $eq: ["$visit_count", 1] }, 1, 0] } }
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
        }
      ]
    }
  }
]);""",
            language="javascript",
        )

# ---------------------------------------------------------------------
# TAB 4: TỐI ƯU COMPOUND INDEX
# ---------------------------------------------------------------------
with tab_index:
    st.subheader("Kiểm Định Hiệu Năng Compound Index Trên MongoDB Atlas")
    st.markdown(
        """
        <p style="font-size: 0.88rem; color: var(--ms-text-muted); margin-bottom: 1.25rem;">
            Truy vấn kiểm thử: <code>db.medical_records.find({ department: 'TIM_MACH' }).sort({ visit_date: -1 })</code> trên tập dữ liệu thực tế <strong>18.186 hồ sơ bệnh án</strong>.
        </p>
        """,
        unsafe_allow_html=True,
    )

    idx_col1, idx_col2 = st.columns(2, gap="medium")

    with idx_col1:
        st.markdown(
            """
            <div style="background: #FFFBEB; border: 1px solid rgba(217, 119, 6, 0.25); border-radius: var(--ms-radius-md); padding: 1.35rem;">
                <span class="ms-badge ms-badge-amber">BEFORE: CHƯA CÓ INDEX</span>
                <h3 style="color: #92400E; margin: 0.75rem 0 0.5rem 0; font-size: 1.5rem;">27 ms</h3>
                <p style="font-size: 0.85rem; color: var(--ms-text-body); margin-bottom: 0.75rem;">
                    Truy vấn buộc phải quét toàn bộ collection trong bộ nhớ:
                </p>
                <ul style="font-size: 0.82rem; color: var(--ms-text-body); margin: 0; padding-left: 1.2rem; line-height: 1.8;">
                    <li>Winning Stage: <strong>SORT</strong> (In-memory sort stage)</li>
                    <li>Input Stage: <strong>COLLSCAN</strong> (Quét toàn bộ bảng)</li>
                    <li>Documents Examined: <strong>18.186 tài liệu</strong></li>
                    <li>Keys Examined: <strong>0 khóa</strong></li>
                    <li>Hạn chế: Tốn RAM, nguy cơ vượt ngưỡng 100MB in-memory sort</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with idx_col2:
        st.markdown(
            """
            <div style="background: #ECFDF5; border: 1px solid rgba(5, 150, 105, 0.25); border-radius: var(--ms-radius-md); padding: 1.35rem;">
                <span class="ms-badge ms-badge-live">AFTER: COMPOUND INDEX</span>
                <h3 style="color: #065F46; margin: 0.75rem 0 0.5rem 0; font-size: 1.5rem;">11 ms (Giảm 59.3%)</h3>
                <p style="font-size: 0.85rem; color: var(--ms-text-body); margin-bottom: 0.75rem;">
                    Index <code>{ department: 1, visit_date: -1 }</code> tuân thủ quy tắc ESR:
                </p>
                <ul style="font-size: 0.82rem; color: var(--ms-text-body); margin: 0; padding-left: 1.2rem; line-height: 1.8;">
                    <li>Winning Stage: <strong>FETCH &larr; IXSCAN</strong></li>
                    <li>Documents Examined: <strong>6.038 tài liệu (Giảm 66.8%)</strong></li>
                    <li>Keys Examined: <strong>6.038 khóa index</strong></li>
                    <li>Loại bỏ hoàn toàn công đoạn SORT in-memory</li>
                    <li>Tốc độ đáp ứng: <strong>Thời gian thực (11ms)</strong></li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)
    with st.expander("Xem chi tiết cấu hình lệnh tạo Index trên MongoDB"):
        st.code(
            """// Tạo Compound Index theo quy tắc Equality -> Sort -> Range (ESR)
db.medical_records.createIndex(
  { department: 1, visit_date: -1 },
  { name: "idx_department_visit_date" }
);

// Đo đạc thực tế bằng executionStats
db.medical_records.find({ department: "TIM_MACH" })
  .sort({ visit_date: -1 })
  .explain("executionStats");""",
            language="javascript",
        )

# =====================================================================
# 6. FOOTER
# =====================================================================
render_workstation_footer()
