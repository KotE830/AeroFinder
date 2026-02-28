"""
크롤러 전략 인터페이스.
"""
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import MonitorUrl

# (airline_id, airline_name, source_url, content_type, raw_content)
CrawlResult = tuple[str, str, str, str, str]


class CrawlerStrategy(Protocol):
    """항공사/사이트별 크롤링 전략. 도메인별로 registry에 등록."""

    async def crawl(
        self,
        session: AsyncSession,
        row: MonitorUrl,
        html: str,
        airline_id: str,
        airline_name: str,
    ) -> list[CrawlResult]:
        """
        목록 페이지 HTML(이미 fetch됨)과 row 정보로 크롤링 후 새 공지만 DB에 저장.
        row.last_html_hash, last_checked_at 은 호출자가 갱신.
        반환: 새로 생성된 공지 목록 [(airline_id, airline_name, source_url, content_type, raw_content), ...]
        """
        ...
