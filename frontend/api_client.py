import requests

# Địa chỉ cơ sở của FastAPI Backend (đã bỏ dấu / ở cuối)
API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# Tránh treo UI nếu backend không phản hồi
REQUEST_TIMEOUT = 30

# =====================================================================
# 1. QUẢN LÝ BỆNH NHÂN (PATIENTS API)
# =====================================================================
def api_get_patients(skip=0, limit=100, search=None):
    params = {"skip": skip, "limit": limit}
    if search:
        params["search"] = search
    try:
        res = requests.get(f"{API_BASE_URL}/patients", params=params, timeout=REQUEST_TIMEOUT)
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
        print(f"API error (list patients): {e}")
        raise e # Ném lỗi lên app.py để hiển thị trạng thái
    return [], 0

def api_create_patient(data: dict):
    try:
        res = requests.post(f"{API_BASE_URL}/patients", json=data, timeout=REQUEST_TIMEOUT)
        return res.json(), res.status_code
    except Exception as e:
        print(f"API error (create patient): {e}")
        return {"detail": str(e)}, 500

def api_update_patient(patient_id: str, data: dict):
    try:
        res = requests.put(f"{API_BASE_URL}/patients/{patient_id}", json=data, timeout=REQUEST_TIMEOUT)
        return res.json(), res.status_code
    except Exception as e:
        print(f"API error (update patient): {e}")
        return {"detail": str(e)}, 500

def api_delete_patient(patient_id: str):
    try:
        res = requests.delete(f"{API_BASE_URL}/patients/{patient_id}", timeout=REQUEST_TIMEOUT)
        return res.status_code
    except Exception as e:
        print(f"API error (delete patient): {e}")
        return 500

def api_get_next_patient_code():
    """Lấy mã bệnh nhân tự động tăng tiếp theo từ Backend."""
    try:
        res = requests.get(f"{API_BASE_URL}/patients/next-code", timeout=REQUEST_TIMEOUT)
        if res.status_code == 200:
            return res.json().get("next_code")
    except Exception as e:
        print(f"API error (get next patient code): {e}")
    return None

# =====================================================================
# 2. QUẢN LÝ HỒ SƠ BỆNH ÁN ĐỘNG (MEDICAL RECORDS API)
# =====================================================================
def api_get_records(skip=0, limit=100, department=None, patient_id=None, search=None, start_date=None, end_date=None):
    params = {"skip": skip, "limit": limit}
    if department:
        params["department"] = department
    if patient_id:
        params["patient_id"] = patient_id
    if search:
        params["search"] = search
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    try:
        res = requests.get(f"{API_BASE_URL}/records", params=params, timeout=REQUEST_TIMEOUT)
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
        print(f"API error (list records): {e}")
        raise e # Ném lỗi lên app.py để hiển thị trạng thái
    return [], 0

def api_create_record(data: dict):
    try:
        res = requests.post(f"{API_BASE_URL}/records", json=data, timeout=REQUEST_TIMEOUT)
        return res.json(), res.status_code
    except Exception as e:
        print(f"API error (create record): {e}")
        return {"detail": str(e)}, 500

def api_update_record(record_id: str, data: dict):
    try:
        res = requests.put(f"{API_BASE_URL}/records/{record_id}", json=data, timeout=REQUEST_TIMEOUT)
        return res.json(), res.status_code
    except Exception as e:
        print(f"API error (update record): {e}")
        return {"detail": str(e)}, 500

def api_delete_record(record_id: str):
    try:
        res = requests.delete(f"{API_BASE_URL}/records/{record_id}", timeout=REQUEST_TIMEOUT)
        return res.status_code
    except Exception as e:
        print(f"API error (delete record): {e}")
        return 500

def api_get_next_record_code():
    """Lấy mã bệnh án tự động tăng tiếp theo từ Backend."""
    try:
        res = requests.get(f"{API_BASE_URL}/records/next-code", timeout=REQUEST_TIMEOUT)
        if res.status_code == 200:
            return res.json().get("next_code")
    except Exception as e:
        print(f"API error (get next record code): {e}")
    return None

# =====================================================================
# 3. THỐNG KÊ Y TẾ (ANALYTICS API)
# =====================================================================
def api_get_department_stats(start_date=None, end_date=None):
    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    res = requests.get(f"{API_BASE_URL}/analytics/departments", params=params, timeout=REQUEST_TIMEOUT)
    res.raise_for_status()
    return res.json()

def api_get_age_groups():
    res = requests.get(f"{API_BASE_URL}/analytics/age-groups", timeout=REQUEST_TIMEOUT)
    res.raise_for_status()
    return res.json()

def api_get_revisit_rate():
    res = requests.get(f"{API_BASE_URL}/analytics/revisit-rate", timeout=REQUEST_TIMEOUT)
    res.raise_for_status()
    return res.json()