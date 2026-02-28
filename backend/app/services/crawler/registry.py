"""
크롤러 전략 등록: slug(항공사 지정) 또는 URL 도메인으로 라우팅.
"""
import logging
from urllib.parse import urlparse

from app.services.crawler.base import CrawlerStrategy
from app.services.crawler.universal import UniversalCrawler

logger = logging.getLogger(__name__)

# 도메인(netloc) -> 전략. 빈 문자열은 기본(universal).
_strategies_by_domain: dict[str, CrawlerStrategy] = {}
# slug(항공사에서 지정) -> 전략. aero_k, jinair, jejuair, parataair 등.
_strategies_by_slug: dict[str, CrawlerStrategy] = {}


def register(domain: str, strategy: CrawlerStrategy) -> None:
    """도메인(예: 'aerok.com')에 전략 등록. 소문자로 저장."""
    _strategies_by_domain[domain.lower().strip()] = strategy


def register_slug(slug: str, strategy: CrawlerStrategy) -> None:
    """slug(예: 'aero_k')에 전략 등록. 항공사.crawler_slug 로 매칭할 때 사용."""
    pass # No longer needed, but keeping signature to avoid breaking existing code just in case, though it's removed from models.


def get_strategy(url: str | None = None) -> CrawlerStrategy:
    """
    이제 무조건 UniversalCrawler를 반환합니다.
    """
    return UniversalCrawler()


def get_strategy_for_url(url: str) -> CrawlerStrategy:
    """URL 도메인만으로 전략 반환 (하위 호환)."""
    return UniversalCrawler()


def _ensure_default() -> None:
    if "" not in _strategies_by_domain:
        _strategies_by_domain[""] = UniversalCrawler()


def _register_builtin_strategies() -> None:
    _ensure_default()
    universal = UniversalCrawler()
    # Backward compatibility for any direct domain references
    register("aerok.com", universal)
    register("jinair.com", universal)
    register("jinair.co.kr", universal)
    register("jejuair.com", universal)
    register("jejuair.co.kr", universal)
    register("twayair.com", universal)
    register("twayair.co.kr", universal)
