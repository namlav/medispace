import re
from datetime import datetime

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.errors import OperationFailure

from backend.app.core.database import get_patients_collection, get_records_collection


def _format_patient(doc: dict) -> dict:
    if not doc:
        return None
    doc["id"] = str(doc["_id"])
    # Bản ghi tạo bằng API cũ có thể thiếu created_at.
    if "created_at" not in doc:
        doc["created_at"] = getattr(doc["_id"], "generation_time", datetime.utcnow())
    return doc


def _object_id(value: str):
    try:
        return ObjectId(value)
    except Exception:
        return None


class PatientService:
    @staticmethod
    def list_patients(skip: int = 0, limit: int = 100, search: str = None):
        patients_col = get_patients_collection()
        query = {}
        if search:
            pattern = re.escape(search)
            query = {
                "$or": [
                    {"full_name": {"$regex": pattern, "$options": "i"}},
                    {"patient_code": {"$regex": pattern, "$options": "i"}},
                    {"phone": {"$regex": pattern, "$options": "i"}}
                ]
            }
        total = patients_col.count_documents(query)
        cursor = patients_col.find(query).skip(skip).limit(limit)
        patients = list(cursor)
        return patients, total

    @staticmethod
    def get_patient_by_id(patient_id: str):
        oid = _object_id(patient_id)
        if not oid:
            return None
        return _format_patient(get_patients_collection().find_one({"_id": oid}))

    @staticmethod
    def get_patient_by_code(patient_code: str):
        return _format_patient(
            get_patients_collection().find_one({"patient_code": patient_code})
        )

    @staticmethod
    def create_patient(patient_in):
        data = patient_in.model_dump()
        data["created_at"] = datetime.utcnow()
        result = get_patients_collection().insert_one(data)
        data["_id"] = result.inserted_id
        return _format_patient(data)

    @staticmethod
    def update_patient(patient_id: str, update_data):
        oid = _object_id(patient_id)
        if not oid:
            return None
        data = update_data.model_dump(exclude_unset=True)
        data.pop("_id", None)
        if not data:
            return PatientService.get_patient_by_id(patient_id)
        updated = get_patients_collection().find_one_and_update(
            {"_id": oid},
            {"$set": data},
            return_document=ReturnDocument.AFTER
        )
        return _format_patient(updated)

    @staticmethod
    def delete_patient(patient_id: str):
        oid = _object_id(patient_id)
        if not oid:
            return False

        patients_col = get_patients_collection()
        records_col = get_records_collection()
        client = patients_col.database.client

        def delete_cascade(session):
            deleted = patients_col.delete_one({"_id": oid}, session=session).deleted_count
            if not deleted:
                return False
            records_col.delete_many({"patient_id": {"$in": [patient_id, oid]}}, session=session)
            return True

        try:
            with client.start_session() as session:
                return session.with_transaction(delete_cascade)
        except OperationFailure as exc:
            # Chỉ fallback khi MongoDB standalone không hỗ trợ transaction.
            if exc.code not in (20, 303):
                raise
            deleted = patients_col.delete_one({"_id": oid}).deleted_count
            if deleted:
                records_col.delete_many({"patient_id": {"$in": [patient_id, oid]}})
            return deleted > 0