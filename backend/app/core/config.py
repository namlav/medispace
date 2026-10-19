import os
from pathlib import Path
from dotenv import load_dotenv

# Tìm file .env ở thư mục gốc project nếu có
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

class Settings:
    PROJECT_NAME: str = "MediSpace - Hệ thống Bệnh án Điện tử NoSQL"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # MongoDB - Lấy trực tiếp từ file .env với giá trị mặc định chuẩn xác
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME: str = os.getenv("DB_NAME", "phongkham_db")
    
    # Collections (Đồng bộ collection lưu bệnh nhân là 'patients')
    PATIENTS_COLLECTION: str = os.getenv("PATIENTS_COLLECTION", "patients")
    RECORDS_COLLECTION: str = os.getenv("RECORDS_COLLECTION", "medical_records")

settings = Settings()