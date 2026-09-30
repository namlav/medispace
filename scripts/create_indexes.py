"""
Script thiết lập Index cho MongoDB và đo lường hiệu năng truy vấn:
1. Single field index:
   - patients.patient_code (unique)
   - medical_records.patient_id
   - medical_records.department
2. Compound index:
   - medical_records.{ department: 1, visit_date: -1 }
3. Đo lường hiệu năng bằng .explain("executionStats")
"""

import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from backend.app.core.database import get_db, get_patients_collection, get_records_collection
import pymongo

def setup_indexes_and_benchmark():
    print("================== BẮT ĐẦU THIẾT LẬP INDEX CHO MONGODB ==================\n")
    patients_col = get_patients_collection()
    records_col = get_records_collection()
    
    # 1. Thử nghiệm truy vấn trước khi có index tổng hợp (Filter department + Sort visit_date)
    print("[1] Đo lường hiệu năng TRƯỚC KHI tạo Compound Index:")
    query_filter = {"department": "TIM_MACH"}
    
    try:
        explain_before = records_col.find(query_filter).sort("visit_date", -1).explain()
        exec_stats_before = explain_before.get("executionStats", {})
        print(f" - Winning Stage: {explain_before.get('queryPlanner', {}).get('winningPlan', {}).get('stage', 'N/A')}")
        print(f" - Documents Examined: {exec_stats_before.get('totalDocsExamined', 'N/A')}")
        print(f" - Execution Time (ms): {exec_stats_before.get('executionTimeMillis', 'N/A')} ms\n")
    except Exception as e:
        print(f"Không thể chạy explain trước index: {e}\n")

    # 2. Tạo Indexes
    print("[2] Đang tạo các chỉ mục tối ưu...")
    # Unique index cho mã bệnh nhân
    idx_patient_code = patients_col.create_index([("patient_code", pymongo.ASCENDING)], unique=True)
    print(f" [✓] Created index on patients: {idx_patient_code}")
    
    # Index tìm kiếm theo tên bệnh nhân (Text index)
    idx_patient_name = patients_col.create_index([("full_name", pymongo.TEXT)])
    print(f" [✓] Created text index on patients: {idx_patient_name}")
    
    # Index tham chiếu bệnh nhân
    idx_rec_patient = records_col.create_index([("patient_id", pymongo.ASCENDING)])
    print(f" [✓] Created index on medical_records: {idx_rec_patient}")
    
    # Compound Index tối ưu hóa truy vấn theo chuyên khoa và sắp xếp theo ngày khám
    idx_compound = records_col.create_index([("department", pymongo.ASCENDING), ("visit_date", pymongo.DESCENDING)])
    print(f" [✓] Created compound index on medical_records: {idx_compound}\n")

    # 3. Đo lường hiệu năng SAU KHI có index
    print("[3] Đo lường hiệu năng SAU KHI tạo Compound Index:")
    try:
        explain_after = records_col.find(query_filter).sort("visit_date", -1).explain()
        exec_stats_after = explain_after.get("executionStats", {})
        print(f" - Winning Stage: {explain_after.get('queryPlanner', {}).get('winningPlan', {}).get('stage', 'N/A')}")
        print(f" - Documents Examined: {exec_stats_after.get('totalDocsExamined', 'N/A')}")
        print(f" - Execution Time (ms): {exec_stats_after.get('executionTimeMillis', 'N/A')} ms\n")
    except Exception as e:
        print(f"Không thể chạy explain sau index: {e}\n")
        
    print("[*] Danh sách toàn bộ index hiện có trong 'medical_records':")
    for idx in records_col.list_indexes():
        print(f" - {idx['name']}: {idx['key']}")
    print("=========================================================================\n")

if __name__ == "__main__":
    setup_indexes_and_benchmark()
