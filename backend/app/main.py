import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import SessionLocal
from app.db.init_db import init_db
from app.api.v1.router import api_router
from app.services.scheduler_service import start_scheduler, stop_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("attendance_backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: auto-initialize tables and seed data if not present
    logger.info("Initializing application lifespan & database...")
    try:
        db = SessionLocal()
        init_db(db)
        db.close()
        logger.info("Database initialization verified successfully.")
    except Exception as e:
        logger.warning(f"Database auto-init note: {e}")

    # Startup APScheduler for period-end absent marking & reporting
    start_scheduler()
    yield
    # Shutdown: gracefully terminate background tasks
    logger.info("Shutting down application...")
    stop_scheduler()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Full-Stack Period-Wise Student Attendance Management System powered by MobileNet Facial Embeddings and SSA-SVM Classification.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# CORS Middleware - allows explicit origins + any local development port
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API V1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["System Health"])
def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["System Health"])
def root_redirect():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs_url": f"{settings.API_V1_STR}/docs",
        "health": "/health",
    }
