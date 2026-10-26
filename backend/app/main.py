import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pymongo.errors import PyMongoError

from backend.app.core.config import settings
from backend.app.core.database import mongo_manager, get_db
from backend.app.api.v1.patients import router as patients_router
from backend.app.api.v1.records import router as records_router
from backend.app.api.v1.analytics import router as analytics_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="REST API cho Hệ thống Bệnh án Điện tử Đa Chuyên Khoa ứng dụng CSDL NoSQL MongoDB"
)

@app.exception_handler(PyMongoError)
async def mongo_exception_handler(request: Request, exc: PyMongoError):
    logger.exception("MongoDB operation failed")
    return JSONResponse(
        status_code=503,
        content={"detail": "Không thể truy cập MongoDB. Vui lòng thử lại sau."}
    )

# Chỉ mở CORS cho các origin được cấu hình, không dùng "*" kèm credentials.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
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
    except Exception:
        mongo_status = "disconnected"
        
    return {
        "api": "healthy",
        "mongodb": mongo_status
    }
