from bson import ObjectId
from datetime import datetime
from typing import List, Optional, Tuple
from backend.app.core.database import get_records_collection
from backend.app.models.record import MedicalRecordCreate, MedicalRecordUpdate

def _format_record(doc: dict) -> dict:
    if not doc:
        return None
    doc["id"] = str(doc["_id"])
    return doc

class RecordService:
    @staticmethod
    def create_record(data: MedicalRecordCreate) -> dict:
        col = get_records_collection()
        doc = data.model_dump()
        doc["created_at"] = datetime.utcnow()
        result = col.insert_one(doc)
        doc["_id"] = result.inserted_id
        return _format_record(doc)

    @staticmethod
    def get_record_by_id(record_id: str) -> Optional[dict]:
        col = get_records_collection()
        try:
            doc = col.find_one({"_id": ObjectId(record_id)})
            return _format_record(doc)
        except Exception:
            return None

    @staticmethod
    def list_records(
        patient_id: Optional[str] = None,
        department: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[dict], int]:
        col = get_records_collection()
        query = {}
        if patient_id:
            query["patient_id"] = patient_id
        if department:
            query["department"] = department
            
        total = col.count_documents(query)
        cursor = col.find(query).sort("visit_date", -1).skip(skip).limit(limit)
        records = [_format_record(d) for d in cursor]
        return records, total

    @staticmethod
    def update_record(record_id: str, data: MedicalRecordUpdate) -> Optional[dict]:
        col = get_records_collection()
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_dict:
            return RecordService.get_record_by_id(record_id)
        
        try:
            res = col.find_one_and_update(
                {"_id": ObjectId(record_id)},
                {"$set": update_dict},
                return_document=True
            )
            return _format_record(res)
        except Exception:
            return None

    @staticmethod
    def delete_record(record_id: str) -> bool:
        col = get_records_collection()
        try:
            res = col.delete_one({"_id": ObjectId(record_id)})
            return res.deleted_count > 0
        except Exception:
            return False
