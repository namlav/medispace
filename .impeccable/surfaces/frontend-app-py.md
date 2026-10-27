---
version: 1
slug: "frontend-app-py"
primary_target: "frontend/app.py"
related_targets: ["frontend/pages/Benh_Nhan.py","frontend/pages/Kham_Benh_Dong.py","frontend/pages/Thong_Ke_Y_Te.py"]
---

# Surface Brief: MediSpace Oceanic Clinical Workstation

## Scope & Mode
- Target: `frontend/app.py`
- Related: `frontend/pages/Benh_Nhan.py`, `frontend/pages/Kham_Benh_Dong.py`, `frontend/pages/Thong_Ke_Y_Te.py`
- Mode: Operate (Clinical Electronic Health Record Workstation)

## Audience & Job
- Primary: Bác sĩ lâm sàng khám bệnh ngoại trú tại phòng khám đa khoa, tiếp nhận hồ sơ, nhập bệnh án chuyên khoa động, kê đơn thuốc và theo dõi diễn tiến điều trị.
- Secondary: Điều dưỡng/tiếp tân tra cứu bệnh nhân, quản lý phòng khám xem chỉ số hiệu năng và báo cáo dịch tễ.

## Direction contract

THESIS: Trạm điều hành lâm sàng xanh nước biển (Oceanic Clinical Command Workstation), từ chối bố cục mặc định sơ sài của Streamlit để tạo nên trải nghiệm phòng khám số hóa cao cấp.

OWN-WORLD: Nền sương biển (#EEF4F9, #FFFFFF), Sidebar màu Abyssal Navy (#0A192F), Ocean Blue Primary (#0284C7), Ocean Cobalt (#075985), và Marine Cyan (#38BDF8). Nhãn định danh BN/BA hiển thị JetBrains Mono tabular.

STORY: Bác sĩ quét mắt nhận diện tức thời trạng thái phòng khám và dữ liệu cốt lõi; chuyển đổi mượt mà giữa tra cứu bệnh nhân, lập hồ sơ khám động 3 chuyên khoa và phân tích số liệu dịch tễ MongoDB quy mô lớn mà không gặp độ trễ.

FIRST VIEWPORT: Phía trên là thanh trạng thái trạm khám lâm sàng (Oceanic Command Bar) với KPI bệnh nhân (10.121) và bệnh án (18.186), kèm chỉ báo kết nối database sống động. Phía dưới là ma trận truy cập nhanh 3 phân hệ chính và bảng giám sát tài nguyên kiến trúc NoSQL.

FORM: Candidate 3 (Oceanic Clinical Command Workstation), seed:d584044fbcbd4aa2

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
