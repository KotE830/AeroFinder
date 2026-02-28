"""
크롤러 공통: HTTP 요청, hash, HTML에서 텍스트/이미지 추출.
"""
import hashlib
import logging
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.config import settings

logger = logging.getLogger(__name__)


def browser_headers(url: str) -> dict[str, str]:
    """요청 URL 기준으로 브라우저처럼 보이는 헤더 (403/404 차단 완화)."""
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": origin + "/",
        "Origin": origin,
        "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin" if url.startswith(origin) else "none",
        "Upgrade-Insecure-Requests": "1",
    }


def _sync_fetch_html_drission(url: str) -> str:
    try:
        from DrissionPage import ChromiumPage, ChromiumOptions
        import time
        
        co = ChromiumOptions()
        co.auto_port()
        co.set_browser_path('/usr/bin/google-chrome')
        co.headless()
        co.set_argument('--window-size=1920,1080')
        co.set_argument('--disable-blink-features=AutomationControlled')
        co.set_argument('--no-sandbox')
        co.set_argument('--disable-gpu')
        co.set_argument('--disable-dev-shm-usage')
        
        page = ChromiumPage(addr_or_opts=co)
        page.set.window.mini() # 화면 최소화
        page.get(url)
        time.sleep(5)
        
        # Cloudflare 대기
        title = str(page.title) if page.title else ""
        html_str = str(page.html) if page.html else ""
        if "challenge" in html_str.lower() or "just a moment" in title.lower() or "잠시만 기다리십시오" in title:
            time.sleep(10)
            
        html = page.html
        page.quit()
        return html
    except Exception as e:
        import logging
        logging.warning(f"fetch_html_drission failed {url}: {e}")
        return ""

async def fetch_html_drission(url: str) -> str:
    """SPA/Bot 차단 사이트를 위해 DrissionPage(강력 우회)로 HTML 반환 (비동기 래핑)."""
    import asyncio
    return await asyncio.to_thread(_sync_fetch_html_drission, url)


async def fetch_html_playwright(url: str) -> str:
    """SPA/Bot 차단 사이트를 위해 Playwright로 HTML 반환 (배경 스레드 이슈 해결위해 sync 버전을 쓰레드로 실행)."""
    import asyncio
    return await asyncio.to_thread(_sync_fetch_html_playwright, url)


async def fetch_html(url: str) -> str:
    """URL의 HTML 본문 반환 (에러 시 빈 문자열). 먼저 httpx, 403이면 Chrome 위장 curl_cffi 재시도."""
    if "jinair.com" in url or "parataair.com" in url or "flyairseoul.com" in url:
        return await fetch_html_drission(url)
        
    headers = browser_headers(url)
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=settings.http_timeout_seconds,
            headers=headers,
        ) as client:
            r = await client.get(url)
            r.raise_for_status()
            return r.text
    except httpx.HTTPStatusError as e:
        if e.response.status_code != 403:
            logger.warning("fetch_html failed %s: %s", url, e)
            return ""
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        # 403 시 curl_cffi로 TLS/헤더 위장. 헤더는 최소로 넘겨서 impersonate가 맞게 채우게 함.
        minimal_headers = {
            "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
            "Referer": origin + "/",
        }
        for impersonate in ("chrome", "safari15_5"):
            try:
                from curl_cffi.requests import AsyncSession as CurlAsyncSession
                async with CurlAsyncSession(impersonate=impersonate) as client:
                    r = await client.get(url, timeout=settings.http_timeout_seconds, headers=minimal_headers)
                    r.raise_for_status()
                    return r.text
            except Exception as e2:
                logger.warning("fetch_html (curl_cffi %s) failed %s: %s", impersonate, url, e2)
        return ""
    except Exception as e:
        logger.warning("fetch_html failed %s: %s", url, e)
        return ""


def compute_hash(html: str) -> str:
    return hashlib.sha256(html.encode("utf-8", errors="replace")).hexdigest()


async def get_notice_content_from_html(html: str, url: str) -> tuple[str, str]:
    """
    HTML에서 공지 영역 텍스트와 첫 번째 큰 이미지(배너) 추출.
    반환: (text_content, image_url_or_empty)
    """
    soup = BeautifulSoup(html, "html.parser")
    text_parts = []
    image_url = ""

    for selector in [
        "article", ".notice", ".board", ".content", "[class*='notice']",
        "[class*='event']", "main", ".detail"
    ]:
        for el in soup.select(selector):
            text_parts.append(el.get_text(separator=" ", strip=True))
            if not image_url:
                img = el.find("img")
                if img and img.get("src"):
                    src = img["src"]
                    if src.startswith("//"):
                        src = "https:" + src
                    elif src.startswith("/"):
                        src = urljoin(url, src)
                    if src.startswith("http") and any(x in src.lower() for x in (".jpg", ".jpeg", ".png", ".webp", ".gif")):
                        image_url = src

    text_content = " ".join(p for p in text_parts if p).strip()
    if not text_content:
        text_content = soup.get_text(separator=" ", strip=True)[:50000]
    return text_content[:100000], image_url
