"""
Thiết lập Index cho MongoDB và đo lường hiệu năng bằng explain("executionStats").

Luồng chạy:
1. Xóa các index do script này quản lý để đưa collection về trạng thái COLLSCAN.
2. Đo truy vấn mẫu (department + khoảng visit_date, sắp xếp giảm dần).
3. Tạo Single Index (patient_id, patient_code, full_name) và Compound Index
   { department: 1, visit_date: -1 }.
4. Đo lại cùng truy vấn và in bảng so sánh trước/sau.

Chạy: python scripts/create_indexes.py
"""

import sys
from datetime import datetime
from pathlib import Path

import pymongo
from pymongo.errors import OperationFailure

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from backend.app.core.database import get_patients_collection, get_records_collection

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Truy vấn mẫu giống bộ lọc của Pipeline 1: một chuyên khoa + khoảng ngày + sort.
QUERY_FILTER = {
    "department": "TIM_MACH",
    "visit_date": {
        "$gte": datetime(2026, 1, 1),
        "$lte": datetime(2026, 12, 31, 23, 59, 59),
    },
}

# Tên index cố định để có thể xóa/tạo lại nhiều lần.
RECORD_INDEX_NAMES = ["patient_id_1", "department_1_visit_date_-1"]
PATIENT_INDEX_NAMES = ["patient_code_1", "full_name_text"]


def winning_stages(plan: dict) -> str:
    """Trả về chuỗi stage của winning plan, ví dụ 'FETCH <- IXSCAN'."""
    stages = []
    node = plan
    while isinstance(node, dict):
        if node.get("stage"):
            stages.append(node["stage"])
        node = node.get("inputStage")
    return " <- ".join(stages) if stages else "UNKNOWN"


def measure_query(records_col) -> dict:
    """Chạy explain (executionStats) cho truy vấn mẫu."""
    # PyMongo >= 4.16 bỏ tham số verbosity; explain() mặc định trả về executionStats.
    # Chạy 1 lần warm-up để loại nhiễu cold cache (dataset nhỏ chỉ ~182 docs).
    records_col.find(QUERY_FILTER).sort("visit_date", -1).explain()
    explain = records_col.find(QUERY_FILTER).sort("visit_date", -1).explain()
    stats = explain.get("executionStats", {})
    return {
        "stages": winning_stages(explain.get("queryPlanner", {}).get("winningPlan", {})),
        "docs_examined": stats.get("totalDocsExamined", 0),
        "keys_examined": stats.get("totalKeysExamined", 0),
        "returned": stats.get("nReturned", 0),
        "execution_ms": stats.get("executionTimeMillis", 0),
    }


def drop_managed_indexes(records_col, patients_col) -> None:
    for col, names in ((records_col, RECORD_INDEX_NAMES), (patients_col, PATIENT_INDEX_NAMES)):
        for name in names:
            try:
                col.drop_index(name)
                print(f" [-] Đã xóa index cũ: {col.name}.{name}")
            except OperationFailure:
                pass  # Index chưa tồn tại.


def create_indexes(records_col, patients_col) -> None:
    print("[2] Tạo các chỉ mục...")
    # patient_code là định danh duy nhất của bệnh nhân trong schema MediSpace (tương đương CCCD).
    print(f" [✓] patients.patient_code (unique): {patients_col.create_index([('patient_code', pymongo.ASCENDING)], unique=True)}")
    print(f" [✓] patients.full_name (text):      {patients_col.create_index([('full_name', pymongo.TEXT)])}")
    print(f" [✓] medical_records.patient_id:     {records_col.create_index([('patient_id', pymongo.ASCENDING)])}")
    compound = records_col.create_index(
        [("department", pymongo.ASCENDING), ("visit_date", pymongo.DESCENDING)]
    )
    print(f" [✓] medical_records.department+visit_date: {compound}\n")


def print_comparison(before: dict, after: dict) -> None:
    rows = [
        ("Winning stage", before["stages"], after["stages"]),
        ("Docs examined", before["docs_examined"], after["docs_examined"]),
        ("Keys examined", before["keys_examined"], after["keys_examined"]),
        ("Docs returned", before["returned"], after["returned"]),
        ("Execution (ms)", before["execution_ms"], after["execution_ms"]),
    ]
    print("+------------------+-------------------------+-------------------------+")
    print("| Tiêu chí         | TRƯỚC khi có Index      | SAU khi có Index        |")
    print("+------------------+-------------------------+-------------------------+")
    for label, old, new in rows:
        print(f"| {label:<16} | {str(old):<23} | {str(new):<23} |")
    print("+------------------+-------------------------+-------------------------+")


def main() -> None:
    print("================== THIẾT LẬP INDEX & ĐO HIỆU NĂNG MONGODB ==================\n")
    records_col = get_records_collection()
    patients_col = get_patients_collection()
    print(f"medical_records: {records_col.count_documents({})} documents")
    print(f"patients:        {patients_col.count_documents({})} documents\n")

    print("[1] Đưa collection về trạng thái chưa có index và đo lường...")
    drop_managed_indexes(records_col, patients_col)
    before = measure_query(records_col)
    print(f" - {before['stages']} | docs={before['docs_examined']} | ms={before['execution_ms']}\n")

    create_indexes(records_col, patients_col)

    print("[3] Đo lại truy vấn mẫu sau khi tạo index...")
    after = measure_query(records_col)
    print(f" - {after['stages']} | docs={after['docs_examined']} | ms={after['execution_ms']}\n")

    print("[4] BẢNG SO SÁNH HIỆU NĂNG")
    print_comparison(before, after)

    print("\n[*] Index hiện có trên medical_records:")
    for idx in records_col.list_indexes():
        print(f" - {idx['name']}: {dict(idx['key'])}")
    print("[*] Index hiện có trên patients:")
    for idx in patients_col.list_indexes():
        print(f" - {idx['name']}: {dict(idx['key'])}")
    print("\n=============================================================================")


if __name__ == "__main__":
    main()
