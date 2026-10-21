from bson import ObjectId
from backend.app.core.database import get_patients_collection

class PatientService:
    @staticmethod
    def list_patients(skip: int = 0, limit: int = 100, search: str = None):
        patients_col = get_patients_collection()
        query = {}
        if search:
            query = {
                "$or": [
                    {"full_name": {"$regex": search, "$options": "i"}},
                    {"patient_code": {"$regex": search, "$options": "i"}},
                    {"phone": {"$regex": search, "$options": "i"}}
                ]
            }
        total = patients_col.count_documents(query)
        cursor = patients_col.find(query).skip(skip).limit(limit)
        patients = list(cursor)
        return patients, total

    @staticmethod
    def create_patient(patient_in):
        patients_col = get_patients_collection()
        if hasattr(patient_in, "model_dump"):
            data = patient_in.model_dump()
        elif hasattr(patient_in, "dict"):
            data = patient_in.dict()
        else:
            data = dict(patient_in)
        result = patients_col.insert_one(data)
        return {"id": str(result.inserted_id)}

    @staticmethod
    def update_patient(patient_id: str, update_data):
        patients_col = get_patients_collection()
        
        # Xử lý an toàn triệt để tránh mọi lỗi liên quan đến model_dump hay dict
        if hasattr(update_data, "model_dump"):
            data = update_data.model_dump()
        elif hasattr(update_data, "dict"):
            data = update_data.dict()
        elif isinstance(update_data, dict):
            data = dict(update_data)
        else:
            data = dict(update_data)
            
        # Loại bỏ _id nếu vô tình dính vào dữ liệu update để tránh lỗi MongoDB
        data.pop("_id", None)
            
        result = patients_col.update_one(
            {"_id": ObjectId(patient_id)},
            {"$set": data}
        )
        return result.modified_count

    @staticmethod
    def delete_patient(patient_id: str):
        patients_col = get_patients_collection()
        result = patients_col.delete_one({"_id": ObjectId(patient_id)})
        return result.deleted_count