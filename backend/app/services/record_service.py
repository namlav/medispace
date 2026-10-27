import re
from bson import ObjectId
from datetime import datetime
from typing import List, Optional, Tuple

from pymongo import ReturnDocument

from backend.app.core.database import get_patients_collection, get_records_collection
from backend.app.models.record import MedicalRecordCreate, MedicalRecordUpdate


def _format_record(doc: dict) -> dict:
    if not doc:
        return None
    doc["id"] = str(doc["_id"])
    return doc


def _object_id(value: str):
    try:
        return ObjectId(value)
    except Exception:
        return None


def _regex(value: str) -> dict:
    return {"$regex": re.escape(value), "$options": "i"}


class RecordService:
    @staticmethod
    def get_next_record_code() -> str:
        """Tự động sinh mã bệnh án tiếp theo (max existing + 1)."""
        col = get_records_collection()
        total = col.count_documents({})
        max_num = total
        for doc in col.find({}, {"record_code": 1}).sort("_id", -1).limit(100):
            code = str(doc.get("record_code", ""))
            nums = re.findall(r"\d+", code)
            if nums:
                max_num = max(max_num, int(nums[-1]))
        next_num = max_num + 1
        code_str = f"{next_num:05d}" if next_num > 9999 else f"{next_num:04d}"
        return f"BA-2026-{code_str}"

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
        oid = _object_id(record_id)
        if not oid:
            return None
        return _format_record(get_records_collection().find_one({"_id": oid}))

    @staticmethod
    def list_records(
        patient_id: Optional[str] = None,
        department: Optional[str] = None,
        search: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[dict], int]:
        col = get_records_collection()
        query = {}
        if patient_id:
            query["patient_id"] = patient_id
        if department:
            query["department"] = department
        if start_date or end_date:
            visit_range = {}
            if start_date:
                visit_range["$gte"] = start_date
            if end_date:
                visit_range["$lte"] = end_date
            query["visit_date"] = visit_range
        if search:
            # shortcut: resolve patient IDs in a second query; move to $lookup
            # if the patients collection no longer fits in memory.
            patient_ids = [
                str(p["_id"])
                for p in get_patients_collection().find(
                    {
                        "$or": [
                            {"full_name": _regex(search)},
                            {"patient_code": _regex(search)}
                        ]
                    },
                    {"_id": 1}
                )
            ]
            conditions = [
                {"record_code": _regex(search)},
                {"doctor_name": _regex(search)},
                {"symptoms": _regex(search)},
                {"diagnosis": _regex(search)}
            ]
            if patient_ids:
                conditions.append({"patient_id": {"$in": patient_ids}})
            query["$or"] = conditions

        total = col.count_documents(query)
        cursor = col.find(query).sort("visit_date", -1).skip(skip).limit(limit)
        records = [_format_record(d) for d in cursor]
        return records, total

    @staticmethod
    def update_record(record_id: str, data: MedicalRecordUpdate) -> Optional[dict]:
        oid = _object_id(record_id)
        if not oid:
            return None
        update_dict = data.model_dump(exclude_unset=True)
        if not update_dict:
            return RecordService.get_record_by_id(record_id)
        updated = get_records_collection().find_one_and_update(
            {"_id": oid},
            {"$set": update_dict},
            return_document=ReturnDocument.AFTER
        )
        return _format_record(updated)

    @staticmethod
    def delete_record(record_id: str) -> bool:
        oid = _object_id(record_id)
        if not oid:
            return False
        return get_records_collection().delete_one({"_id": oid}).deleted_count > 0
