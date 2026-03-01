"""
5~10분 간격 공지 감지 파이프라인 실행
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.services.pipeline import run_pipeline

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


def start_scheduler():
    interval_seconds = max(300, settings.crawl_interval_seconds) #최소 5분 이상 보장, 상한선 해제
    scheduler.add_job(run_pipeline, "interval", seconds=interval_seconds, id="notice_detection")
    scheduler.start()
    logger.info("Scheduler started: notice_detection every %s seconds", interval_seconds)


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
