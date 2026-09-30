from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from backend.app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class MongoManager:
    client: MongoClient = None
    db: Database = None

    def connect(self):
        try:
            self.client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
            self.db = self.client[settings.DB_NAME]
            # Ping thử kết nối
            self.client.admin.command('ping')
            logger.info(f"Kết nối thành công đến MongoDB: {settings.DB_NAME}")
        except Exception as e:
            logger.warning(f"Chưa kết nối được tới MongoDB ({e}). Vui lòng kiểm tra lại MONGO_URI.")

    def close(self):
        if self.client:
            self.client.close()
            logger.info("Đã đóng kết nối MongoDB.")

mongo_manager = MongoManager()

def get_db() -> Database:
    if mongo_manager.db is None:
        mongo_manager.connect()
    return mongo_manager.db

def get_patients_collection() -> Collection:
    db = get_db()
    return db[settings.PATIENTS_COLLECTION]

def get_records_collection() -> Collection:
    db = get_db()
    return db[settings.RECORDS_COLLECTION]
