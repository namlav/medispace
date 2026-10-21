import requests

# Địa chỉ cơ sở của FastAPI Backend (đã bỏ dấu / ở cuối)
API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# =====================================================================
# 1. QUẢN LÝ BỆNH NHÂN (PATIENTS API)
# =====================================================================
def api_get_patients(skip=0, limit=100, search=None):
    params = {"skip": skip, "limit": limit}
    if search:
        params["search"] = search
    try:
        res = requests.get(f"{API_BASE_URL}/patients", params=params)
        res.raise_for_status() # Ép văng lỗi nếu Backend trả về 4xx, 5xx
        
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, dict):
                items = data.get("items") or data.get("data") or []
                total = data.get("total") or len(items)
                return items, total
            elif isinstance(data, list):
                return data, len(data)
    except Exception as e:
        print(f"Lỗi kết nối API lấy danh sách bệnh nhân: {e}")
        raise e # Ném lỗi lên app.py để hiển thị trạng thái
    return [], 0

def api_create_patient(data: dict):
    try:
        res = requests.post(f"{API_BASE_URL}/patients", json=data)
        return res.json(), res.status_code
    except Exception as e:
        print(f"Lỗi kết nối API tạo bệnh nhân: {e}")
        return {"detail": str(e)}, 500

def api_update_patient(patient_id: str, data: dict):
    try:
        res = requests.put(f"{API_BASE_URL}/patients/{patient_id}", json=data)
        return res.json(), res.status_code
    except Exception as e:
        print(f"Lỗi kết nối API cập nhật bệnh nhân: {e}")
        return {"detail": str(e)}, 500

def api_delete_patient(patient_id: str):
    try:
        res = requests.delete(f"{API_BASE_URL}/patients/{patient_id}")
        return res.status_code
    except Exception as e:
        print(f"Lỗi kết nối API xóa bệnh nhân: {e}")
        return 500

# =====================================================================
# 2. QUẢN LÝ HỒ SƠ BỆNH ÁN ĐỘNG (MEDICAL RECORDS API)
# =====================================================================
def api_get_records(skip=0, limit=100, department=None):
    params = {"skip": skip, "limit": limit}
    if department:
        params["department"] = department
    try:
        res = requests.get(f"{API_BASE_URL}/records", params=params)
        res.raise_for_status() # Ép văng lỗi nếu Backend trả về 4xx, 5xx
        
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, dict):
                items = data.get("items") or data.get("data") or []
                total = data.get("total") or len(items)
                return items, total
            elif isinstance(data, list):
                return data, len(data)
    except Exception as e:
        print(f"Lỗi kết nối API lấy danh sách bệnh án: {e}")
        raise e # Ném lỗi lên app.py để hiển thị trạng thái
    return [], 0

def api_create_record(data: dict):
    try:
        res = requests.post(f"{API_BASE_URL}/records", json=data)
        return res.json(), res.status_code
    except Exception as e:
        print(f"Lỗi kết nối API tạo bệnh án: {e}")
        return {"detail": str(e)}, 500

def api_update_record(record_id: str, data: dict):
    try:
        res = requests.put(f"{API_BASE_URL}/records/{record_id}", json=data)
        return res.json(), res.status_code
    except Exception as e:
        print(f"Lỗi kết nối API cập nhật bệnh án: {e}")
        return {"detail": str(e)}, 500

def api_delete_record(record_id: str):
    try:
        res = requests.delete(f"{API_BASE_URL}/records/{record_id}")
        return res.status_code
    except Exception as e:
        print(f"Lỗi kết nối API xóa bệnh án: {e}")
        return 500