"""
AeroFinder Backend API
국내 항공사 특가 이벤트: 공지 감지 → 분석 → 앱 푸시
"""
import logging
from contextlib import asynccontextmanager
import os
import firebase_admin
from firebase_admin import credentials

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, airlines, deals, keywords, notices
from app.config import settings as app_settings
from app.db import init_db
from app.scheduler import start_scheduler, stop_scheduler

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Firebase Admin SDK
    try:
        if os.path.exists(app_settings.firebase_credentials_path):
            cred = credentials.Certificate(app_settings.firebase_credentials_path)
            firebase_admin.initialize_app(cred)
            logger.info(f"Firebase Admin SDK initialized with {app_settings.firebase_credentials_path}")
        else:
            logger.warning(f"Firebase credentials not found at '{app_settings.firebase_credentials_path}'. Push notifications will fail.")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")

    try:
        await init_db()
        start_scheduler()
    except Exception as e:
        logger.warning("DB 연결 실패로 DB/스케줄러 없이 시작합니다. PostgreSQL 설치·실행 후 재시작하세요: %s", e)
    yield
    stop_scheduler()


app = FastAPI(
    title="AeroFinder API",
    description="국내 항공사 특가·이벤트 정보 API (공지 감지 → 분석 → 푸시)",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=(["*"] if app_settings.cors_origins.strip() == "*" else [x.strip() for x in app_settings.cors_origins.split(",") if x.strip()]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(deals.router, prefix="/api/deals", tags=["deals"])
app.include_router(airlines.router, prefix="/api/airlines", tags=["airlines"])
app.include_router(keywords.router, prefix="/api/keywords", tags=["keywords"])
app.include_router(notices.router, prefix="/api/notices", tags=["notices"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.get("/health")
def health_check():
    """서버 상태 확인"""
    return {"status": "ok"}
