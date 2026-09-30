from bson import ObjectId
from datetime import datetime
from typing import List, Optional, Tuple
from backend.app.core.database import get_patients_collection
from backend.app.models.patient import PatientCreate, PatientUpdate

def _format_patient(doc: dict) -> dict:
    if not doc:
        return None
    doc["id"] = str(doc["_id"])
    return doc

class PatientService:
    @staticmethod
    def create_patient(data: PatientCreate) -> dict:
        col = get_patients_collection()
        doc = data.model_dump()
        doc["created_at"] = datetime.utcnow()
        result = col.insert_one(doc)
        doc["_id"] = result.inserted_id
        return _format_patient(doc)

    @staticmethod
    def get_patient_by_id(patient_id: str) -> Optional[dict]:
        col = get_patients_collection()
        try:
            doc = col.find_one({"_id": ObjectId(patient_id)})
            return _format_patient(doc)
        except Exception:
            return None

    @staticmethod
    def get_patient_by_code(patient_code: str) -> Optional[dict]:
        col = get_patients_collection()
        doc = col.find_one({"patient_code": patient_code})
        return _format_patient(doc)

    @staticmethod
    def list_patients(skip: int = 0, limit: int = 50, search: Optional[str] = None) -> Tuple[List[dict], int]:
        col = get_patients_collection()
        query = {}
        if search:
            query = {
                "$or": [
                    {"full_name": {"$regex": search, "$options": "i"}},
                    {"patient_code": {"$regex": search, "$options": "i"}},
                    {"phone": {"$regex": search, "$options": "i"}}
                ]
            }
        total = col.count_documents(query)
        cursor = col.find(query).sort("created_at", -1).skip(skip).limit(limit)
        patients = [_format_patient(d) for d in cursor]
        return patients, total

    @staticmethod
    def update_patient(patient_id: str, data: PatientUpdate) -> Optional[dict]:
        col = get_patients_collection()
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_dict:
            return PatientService.get_patient_by_id(patient_id)
        
        try:
            res = col.find_one_and_update(
                {"_id": ObjectId(patient_id)},
                {"$set": update_dict},
                return_document=True
            )
            return _format_patient(res)
        except Exception:
            return None

    @staticmethod
    def delete_patient(patient_id: str) -> bool:
        col = get_patients_collection()
        try:
            res = col.delete_one({"_id": ObjectId(patient_id)})
            return res.deleted_count > 0
        except Exception:
            return False
