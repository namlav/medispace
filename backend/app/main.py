from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import mongo_manager, get_db
from backend.app.api.v1.patients import router as patients_router
from backend.app.api.v1.records import router as records_router
from backend.app.api.v1.analytics import router as analytics_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="REST API cho Hệ thống Bệnh án Điện tử Đa Chuyên Khoa ứng dụng CSDL NoSQL MongoDB"
)

# Cấu hình CORS để Frontend (Streamlit / React / Vue) có thể gọi thoải mái
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_db_client():
    mongo_manager.connect()

@app.on_event("shutdown")
def shutdown_db_client():
    mongo_manager.close()

# Include routers
app.include_router(patients_router, prefix=settings.API_V1_PREFIX)
app.include_router(records_router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics_router, prefix=settings.API_V1_PREFIX)

@app.get("/", tags=["Health Check"])
def root():
    return {
        "status": "online",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

@app.get("/health", tags=["Health Check"])
def health_check():
    try:
        db = get_db()
        db.command("ping")
        mongo_status = "connected"
    except Exception as e:
        mongo_status = f"disconnected: {str(e)}"
        
    return {
        "api": "healthy",
        "mongodb": mongo_status
    }
