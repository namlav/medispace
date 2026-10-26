import os
from pathlib import Path
from dotenv import load_dotenv

# Tìm file .env ở thư mục gốc project nếu có
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
env_path = BASE_DIR / ".env"

# Local: .env thắng biến môi trường cũ trên máy.
# Production: đặt APP_ENV=production để biến môi trường OS thắng .env.
load_dotenv(dotenv_path=env_path, override=False)
if os.getenv("APP_ENV", "development").lower() != "production":
    load_dotenv(dotenv_path=env_path, override=True)


class Settings:
    PROJECT_NAME: str = "MediSpace - Hệ thống Bệnh án Điện tử NoSQL"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # MongoDB - Lấy trực tiếp từ file .env với giá trị mặc định chuẩn xác
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME: str = os.getenv("DB_NAME", "medispace_db")

    # Collections (Đồng bộ collection lưu bệnh nhân là 'patients')
    PATIENTS_COLLECTION: str = os.getenv("PATIENTS_COLLECTION", "patients")
    RECORDS_COLLECTION: str = os.getenv("RECORDS_COLLECTION", "medical_records")

    # Chỉ các origin này được gọi API từ trình duyệt.
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:8501,http://127.0.0.1:8501",
        ).split(",")
        if origin.strip()
    ]


settings = Settings()
