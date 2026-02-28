"""
공지 분석: 키워드로 특가 여부 판별, 날짜/노선 추출.
- 텍스트: 키워드 포함 여부 + 정규식으로 행사 기간 추출
- 이미지: EasyOCR → (선택) Gemini/GPT로 파편 텍스트에서 기간 JSON 추출
"""
import asyncio
import re
import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.db_models import Airline, Keyword, Notice, Deal

logger = logging.getLogger(__name__)

# 행사 기간 패턴 (한국어/숫자)
DATE_PATTERNS = [
    re.compile(r"(\d{4})\s*[\.\-/]\s*(\d{1,2})\s*[\.\-/]\s*(\d{1,2})\s*[-~]\s*(\d{4})\s*[\.\-/]\s*(\d{1,2})\s*[\.\-/]\s*(\d{1,2})"),
    re.compile(r"(\d{4})\s*[\.\-/]\s*(\d{1,2})\s*[\.\-/]\s*(\d{1,2})\s*까지"),
    re.compile(r"(\d{1,2})\s*[\.\-/]\s*(\d{1,2})\s*[-~]\s*(\d{1,2})\s*[\.\-/]\s*(\d{1,2})"),
    re.compile(r"~?\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일\s*까지"),
    re.compile(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일\s*[-~]"),
]


def _parse_date_from_match(m: re.Match, pattern_index: int) -> tuple[datetime | None, datetime | None]:
    g = m.groups()
    try:
        from datetime import timezone
        if pattern_index == 0 and len(g) >= 6:
            start = datetime(int(g[0]), int(g[1]), int(g[2]), tzinfo=timezone.utc)
            end = datetime(int(g[3]), int(g[4]), int(g[5]), 23, 59, 59, tzinfo=timezone.utc)
            return start, end
        if pattern_index == 1 and len(g) >= 3:
            end = datetime(int(g[0]), int(g[1]), int(g[2]), 23, 59, 59, tzinfo=timezone.utc)
            return None, end
        if pattern_index == 2 and len(g) >= 4:
            y = datetime.now().year
            start = datetime(y, int(g[0]), int(g[1]), tzinfo=timezone.utc)
            end = datetime(y, int(g[2]), int(g[3]), 23, 59, 59, tzinfo=timezone.utc)
            return start, end
        if pattern_index == 3 and len(g) >= 2:
            y = datetime.now().year
            mth, day = int(g[0]), int(g[1])
            end = datetime(y, mth, day, 23, 59, 59, tzinfo=timezone.utc)
            return None, end
        if pattern_index == 4 and len(g) >= 3:
            start = datetime(int(g[0]), int(g[1]), int(g[2]), tzinfo=timezone.utc)
            return start, None
    except (ValueError, IndexError):
        pass
    return None, None


def extract_event_dates_from_text(text: str) -> tuple[datetime | None, datetime | None]:
    """텍스트에서 행사 기간 추출."""
    for i, pat in enumerate(DATE_PATTERNS):
        m = pat.search(text)
        if m:
            return _parse_date_from_match(m, i)
    return None, None


async def get_keywords_for_airline(session: AsyncSession, airline_id: str) -> list[str]:
    """항공사 전용 + airline_id NULL(공통) 키워드."""
    q = select(Keyword.keyword).where(
        (Keyword.airline_id == airline_id) | (Keyword.airline_id.is_(None))
    )
    res = await session.execute(q)
    return [r[0] for r in res.fetchall()]


def is_special_deal_by_keywords(text: str, keywords: list[str]) -> bool:
    if not keywords:
        return False
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


async def analyze_text_notice(session: AsyncSession, notice: Notice) -> bool:
    """텍스트 공지 분석: 키워드 확인 + 기간 추출. 특가면 True."""
    keywords = await get_keywords_for_airline(session, notice.airline_id)
    text = (notice.raw_content or "")[:50000]
    if not is_special_deal_by_keywords(text, keywords):
        return False
    start, end = extract_event_dates_from_text(text)
    notice.extracted_text = text[:10000]
    if not notice.event_start:
        notice.event_start = start
    if not notice.event_end:
        notice.event_end = end
    notice.is_special_deal = True
    notice.analyzed_at = datetime.utcnow()
    return True


def _extract_routes_simple(text: str) -> list[str] | None:
    """간단한 노선 패턴 (예: ICN-GMP, 김포-제주)."""
    route_pat = re.compile(r"[A-Z]{3}\s*[-~]\s*[A-Z]{3}|김포\s*[-~]\s*제주|인천\s*[-~]\s*제주|제주\s*[-~]\s*김포")
    found = route_pat.findall(text)
    return list(set(found)) if found else None


async def analyze_image_notice(session: AsyncSession, notice: Notice) -> bool:
    """이미지 분석 기능은 제거됨. 항상 False를 반환합니다."""
    logger.info("Image analysis is intentionally disabled. Skipping notice %s", notice.id)
    return False


async def analyze_notice(session: AsyncSession, notice: Notice) -> bool:
    """공지 타입에 따라 분석. 특가로 판단되면 True."""
    if notice.content_type == "text":
        return await analyze_text_notice(session, notice)
    if notice.content_type == "image":
        return await analyze_image_notice(session, notice)
    return False


async def push_notice_to_deal(session: AsyncSession, notice: Notice) -> Deal | None:
    """특가 공지를 Deal로 만들어 앱에 푸시(DB 저장)."""
    if not notice.is_special_deal:
        return None
    ar = await session.execute(select(Airline).where(Airline.id == notice.airline_id))
    airline = ar.scalar_one_or_none()
    if not airline:
        return None
    title = notice.extracted_text.strip() if notice.extracted_text and notice.extracted_text.strip() else f"{airline.name} 특가"
    if title == "공지" or title == airline.name:
        title = f"{airline.name} 특가"

    deal = Deal(
        notice_id=notice.id,
        airline_id=notice.airline_id,
        title=title,
        description=notice.extracted_text[:500] if notice.extracted_text and notice.extracted_text != title else None,
        url=notice.source_url,
        event_start=notice.event_start,
        event_end=notice.event_end,
        routes=notice.routes,
        image_url=notice.raw_content if notice.content_type == "image" else None,
    )
    session.add(deal)
    await session.flush()
    return deal
