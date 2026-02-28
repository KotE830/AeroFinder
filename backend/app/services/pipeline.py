"""
파이프라인: 공지 감지 → 분석 → 앱 푸시(Deal 저장)
"""
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import AsyncSessionLocal
from app.models.db_models import Notice
from app.services.crawler import run_notice_detection
from app.services.analyzer import analyze_notice, push_notice_to_deal

logger = logging.getLogger(__name__)


async def run_pipeline():
    """한 사이클: hash 감지 → 새 공지 분석 → 특가면 Deal 생성."""
    async with AsyncSessionLocal() as session:
        try:
            new_notices = await run_notice_detection(session)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.exception("notice_detection failed: %s", e)
            return

    for airline_id, airline_name, source_url, content_type, raw_content in new_notices:
        async with AsyncSessionLocal() as session:
            try:
                # 방금 생성된 공지 조회 (source_url + airline_id로)
                q = select(Notice).where(
                    Notice.airline_id == airline_id,
                    Notice.source_url == source_url,
                ).order_by(Notice.created_at.desc()).limit(1)
                res = await session.execute(q)
                notice = res.scalar_one_or_none()
                if not notice:
                    continue
                ok = await analyze_notice(session, notice)
                if ok:
                    await push_notice_to_deal(session, notice)
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.exception("analyze/push failed for %s: %s", source_url, e)
