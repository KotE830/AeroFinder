"""
오픈 직후 실제 가격 크롤링 → Deal.price 업데이트 (앱에 푸시된 후 호출)
항공사/페이지별 선택자는 DB 또는 설정으로 확장 가능.
"""
import logging
import re
from decimal import Decimal

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.db_models import Deal

logger = logging.getLogger(__name__)

# 항공사별 가격 추출 정규식 또는 CSS 선택자 (추후 DB/설정으로 이전 가능)
PRICE_PATTERNS = [
    re.compile(r"(\d{1,3}(?:,\d{3})*)\s*원"),
    re.compile(r"₩\s*(\d{1,3}(?:,\d{3})*)"),
    re.compile(r"(\d+)\s*원"),
]


async def fetch_price_from_url(url: str) -> Decimal | None:
    """URL 페이지에서 가격 숫자 추출 (첫 번째 매칭)."""
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=settings.http_timeout_seconds,
        ) as client:
            r = await client.get(url)
            r.raise_for_status()
            text = r.text
    except Exception as e:
        logger.warning("fetch_price_from_url failed %s: %s", url, e)
        return None
    for pat in PRICE_PATTERNS:
        m = pat.search(text)
        if m:
            try:
                raw = m.group(1).replace(",", "")
                return Decimal(raw)
            except Exception:
                continue
    return None


async def update_deal_prices(session: AsyncSession, deal_id: str | None = None) -> int:
    """
    price가 비어 있는 Deal에 대해 URL 크롤링으로 가격 채우기.
    deal_id가 있으면 해당 건만, 없으면 전부.
    반환: 업데이트된 건수.
    """
    q = select(Deal).where(Deal.price.is_(None))
    if deal_id:
        q = q.where(Deal.id == deal_id)
    res = await session.execute(q)
    deals = res.scalars().all()
    updated = 0
    for d in deals:
        price = await fetch_price_from_url(d.url)
        if price is not None:
            d.price = price
            updated += 1
    return updated
