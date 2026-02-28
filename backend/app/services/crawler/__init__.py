"""
크롤러 패키지: 항공사/도메인별 전략 패턴.
- run_notice_detection(session) → 새 공지 목록
- fetch_html, compute_hash, get_notice_content_from_html (공통 유틸)
"""
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import Airline, MonitorUrl

from app.services.crawler.base import CrawlResult, CrawlerStrategy
from app.services.crawler.common import (
    compute_hash,
    fetch_html,
    get_notice_content_from_html,
)
from app.services.crawler.registry import get_strategy, get_strategy_for_url, register

logger = logging.getLogger(__name__)

# 기본 전략 + 항공사별 전략 등록 (도메인으로 라우팅)
from app.services.crawler.registry import _register_builtin_strategies
_register_builtin_strategies()


async def run_notice_detection(session: AsyncSession) -> list[CrawlResult]:
    """
    모든 MonitorUrl에 대해: URL 도메인별 전략으로 크롤링.
    반환: 새 공지 목록 [(airline_id, airline_name, source_url, content_type, raw_content), ...]
    """
    result: list[CrawlResult] = []
    q = select(MonitorUrl).join(Airline)
    res = await session.execute(q)
    rows = res.scalars().all()

    for row in rows:
        url = row.url
        airline_id = row.airline_id
        html = await fetch_html(url)
        if not html:
            logger.warning("크롤링 스킵(HTML 수집 실패): %s", url)
            continue
        airline_q = select(Airline).where(Airline.id == airline_id)
        ar = await session.execute(airline_q)
        airline = ar.scalar_one_or_none()
        airline_name = airline.name if airline else ""

        strategy = get_strategy(url=url)
        logger.info("크롤링 %s: %s", airline_name or airline_id, type(strategy).__name__)
        part = await strategy.crawl(session, row, html, airline_id, airline_name)
        if part:
            logger.info("  → 새 공지 %d건: %s", len(part), [p[2][:60] + "..." if len(p[2]) > 60 else p[2] for p in part])
        result.extend(part)

    return result


__all__ = [
    "run_notice_detection",
    "fetch_html",
    "compute_hash",
    "get_notice_content_from_html",
    "register",
    "get_strategy",
    "get_strategy_for_url",
    "CrawlerStrategy",
    "CrawlResult",
]
