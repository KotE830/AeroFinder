"""
범용 크롤러: DB에 저장된 list_link_selector / detail_title_selector 또는 자동 추정으로 목록→상세 또는 단일 페이지 hash 비교.
"""
from collections import Counter
from datetime import datetime
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import Airline, MonitorUrl, Notice

from app.services.crawler.base import CrawlResult
from app.services.crawler.common import compute_hash, fetch_html, get_notice_content_from_html


def _normalize_link_selector(value: str) -> str:
    """웹에서 'ul' → 'ul > a', 'div' → 'div > a', class명만 넣으면 '.{class}'로 변환."""
    s = (value or "").strip()
    if not s:
        return s
    if s.lower() == "ul":
        return "ul > a"
    if s.lower() == "div":
        return "div > a"
    if not any(c in s for c in " []():>+~#."):
        return f".{s}"
    return s


def _extract_detail_links(html: str, list_url: str, selector: str) -> list[str]:
    """목록 페이지 HTML에서 상세 페이지 링크 추출 (절대 URL)."""
    soup = BeautifulSoup(html, "html.parser")
    urls: list[str] = []
    resolved = _normalize_link_selector(selector)
    if not resolved:
        return urls
    try:
        for el in soup.select(resolved):
            if el.name == "a":
                href = el.get("href")
            else:
                a = el.find("a")
                href = a.get("href") if a else None
            if not href or not str(href).strip():
                continue
            full = urljoin(list_url, str(href).strip())
            if full.startswith("http") and full not in urls:
                urls.append(full)
    except Exception:
        pass
    if not urls and " " in resolved and resolved.startswith("li."):
        fallback = resolved.replace("li.", ".", 1)
        try:
            for el in soup.select(fallback):
                if el.name == "a":
                    href = el.get("href")
                else:
                    a = el.find("a")
                    href = a.get("href") if a else None
                if not href or not str(href).strip():
                    continue
                full = urljoin(list_url, str(href).strip())
                if full.startswith("http") and full not in urls:
                    urls.append(full)
        except Exception:
            pass
    return urls


def _normalize_title_selector(value: str | None) -> str | None:
    """웹에서 'div' 입력 시 제목이 div 안의 strong에 있으면 'div strong'으로 해석."""
    s = (value or "").strip()
    if not s:
        return None
    if s.lower() == "div":
        return "div strong"
    return s


def _extract_detail_title(html: str, title_selector: str | None = None) -> str:
    """상세 페이지 HTML에서 제목 추출."""
    soup = BeautifulSoup(html, "html.parser")

    def _text_from_selector(sel: str) -> str | None:
        try:
            els = soup.select(sel)
            if els:
                t = els[0].get_text(strip=True)
                if t:
                    return t[:500]
        except Exception:
            pass
        return None

    sel = _normalize_title_selector(title_selector) if title_selector else None
    if sel:
        t = _text_from_selector(sel)
        if t:
            return t
    if "chakra-text" in html:
        t = _text_from_selector("h1.chakra-text")
        if t:
            return t
    if soup.title and soup.title.string:
        return soup.title.string.strip()[:500]
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        return og["content"].strip()[:500]
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)[:500]
    return "공지"


def _normalize_url(u: str) -> str:
    u = (u or "").strip().rstrip("/")
    if "#" in u:
        u = u.split("#")[0].rstrip("/")
    return u


def get_link_from_el(el, list_url: str):
    import re
    # 1. ParataAir specific check (data-event-seq-no)
    for node in [el] + el.find_all(True):
        seq = node.get("data-event-seq-no")
        if seq:
            return urljoin(list_url, f"/ko/contents/event/viewEventList.do?eventSeqNo={seq}")

    # 2. Try finding an 'a' tag
    for a in [el] + el.find_all("a"):
        href = a.get("href")
        if href and href != "#" and not href.startswith("javascript:void"):
            if href.startswith("javascript:"):
                m = re.search(r"'(.*?)'", href) or re.search(r'"(.*?)"', href)
                if m: return urljoin(list_url, m.group(1))
            return urljoin(list_url, str(href).strip())
    
    # 3. Try finding onclick
    for node in [el] + el.find_all(True):
        onclick = node.get("onclick")
        if onclick:
            m = re.search(r"'(.*?)'", onclick) or re.search(r'"(.*?)"', onclick)
            if m:
                val = m.group(1)
                if "/" in val or ".do" in val or "http" in val:
                    return urljoin(list_url, val.strip())
    return None


def parse_event_period(text: str) -> tuple[datetime | None, datetime | None]:
    if not text:
        return None, None
    import re
    # match patterns like "2026.01.01", "26.01.01", "01.01", "2026/01/01", "2026-01-01"
    pattern = r'(?:(?:20)?(\d{2})[./-])?(\d{1,2})[./-](\d{1,2})'
    matches = re.findall(pattern, text)
    if len(matches) >= 2:
        try:
            from datetime import timezone
            start_y, start_m, start_d = matches[0]
            end_y, end_m, end_d = matches[1]
            
            curr_year = datetime.utcnow().year
            sy = 2000 + int(start_y) if start_y else curr_year
            ey = 2000 + int(end_y) if end_y else curr_year
            
            if not start_y and not end_y and int(start_m) > int(end_m):
                ey += 1
            
            start_dt = datetime(sy, int(start_m), int(start_d), tzinfo=timezone.utc)
            end_dt = datetime(ey, int(end_m), int(end_d), 23, 59, 59, tzinfo=timezone.utc)
            return start_dt, end_dt
        except ValueError:
            pass
    return None, None


def extract_links_and_titles_from_list_page(
    html: str,
    list_url: str,
    list_selector: str,
    title_selector: str,
    period_selector: str | None = None,
    container_tag: str = "parent",
) -> list[tuple[str, str, str | None]]:
    """
    목록 페이지에서 (상세 URL, 제목, 기간텍스트) 쌍 추출.
    """
    soup = BeautifulSoup(html, "html.parser")
    resolved_list = _normalize_link_selector(list_selector)
    title_sel = _normalize_link_selector(title_selector)
    period_sel = _normalize_link_selector(period_selector) if period_selector else None
    result: list[tuple[str, str, str | None]] = []
    try:
        elements = soup.select(resolved_list)
        for el in elements:
            href = get_link_from_el(el, list_url)
            if not href or not href.startswith("http"):
                continue

            if container_tag == "li":
                container = el.find_parent("li") or el
            else:
                container = el
            
            title_el = container.select_one(title_sel) if title_sel else None
            period_el = container.select_one(period_sel) if period_sel else None
            
            period_text = period_el.get_text(separator=" ", strip=True) if period_el else None

            # Robust title check
            title = "공지"
            if title_el:
                raw_text = title_el.get_text(separator=" ", strip=True)
                if raw_text and len(raw_text) > 2 and len(raw_text) < 150:
                    import re
                    if re.search(r'[a-zA-Z0-9가-힣]', raw_text):
                        title = raw_text
                        
            result.append((href, title, period_text))
    except Exception as e:
        import logging
        logging.error(f"extract_links_and_titles failed: {e}")
    return result


class UniversalCrawler:
    """단일 웹 컴포넌트 경로로 목록 및 상세 페이지 크롤링 수행."""

    async def crawl(
        self,
        session: AsyncSession,
        row: MonitorUrl,
        html: str,
        airline_id: str,
        airline_name: str,
    ) -> list[CrawlResult]:
        result: list[CrawlResult] = []
        new_hash = compute_hash(html)
        now = datetime.utcnow()

        selector = (row.list_link_selector or "").strip()
        title_selector = (row.detail_title_selector or "").strip()

        if selector:
            part = await self._crawl_list_detail(
                session, row, html, airline_id, airline_name, selector, title_selector
            )
            result.extend(part)
        else:
            is_first = row.last_html_hash is None
            is_changed = row.last_html_hash is not None and row.last_html_hash != new_hash
            if is_first or is_changed:
                text_content, image_url = await get_notice_content_from_html(html, row.url)
                if image_url and len(text_content) < 200:
                    content_type = "image"
                    raw_content = image_url
                else:
                    content_type = "text"
                    raw_content = text_content or html[:50000]
                notice = Notice(
                    airline_id=airline_id,
                    source_url=row.url,
                    content_type=content_type,
                    raw_content=raw_content,
                    is_special_deal=False,
                )
                session.add(notice)
                await session.flush()
                result.append((airline_id, airline_name, row.url, content_type, raw_content))

        row.last_html_hash = new_hash
        row.last_checked_at = now
        return result

    async def _crawl_list_detail(
        self,
        session: AsyncSession,
        row: MonitorUrl,
        html: str,
        airline_id: str,
        airline_name: str,
        selector: str,
        title_selector: str,
    ) -> list[CrawlResult]:
        result: list[CrawlResult] = []
        
        existing = await session.execute(
            select(Notice.source_url).where(Notice.airline_id == airline_id)
        )
        seen = {r[0] for r in existing.fetchall()}
        
        list_page_norm = _normalize_url(row.url)
        all_items = []
        current_html = html
        current_url = row.url
        max_pages = 10
        pages_crawled = 0
        
        while current_html and pages_crawled < max_pages:
            pages_crawled += 1
            # 1. 목록 페이지에서 (URL, 제목, 기간) 추출 시도
            page_items = extract_links_and_titles_from_list_page(
                current_html, current_url, selector, title_selector, row.list_period_selector
            )
            
            valid_items = [(u, t, p) for u, t, p in page_items if _normalize_url(u) != list_page_norm]
            if not valid_items:
                break
                
            all_items.extend(valid_items)
            
            found_existing = any(u in seen for u, t, p in valid_items)
            if found_existing:
                break
                
            if row.list_next_selector:
                soup = BeautifulSoup(current_html, "html.parser")
                next_btn = soup.select_one(row.list_next_selector)
                next_href = get_link_from_el(next_btn, current_url) if next_btn else None
                if next_href and _normalize_url(next_href) != _normalize_url(current_url):
                    current_url = next_href
                    current_html = await fetch_html(current_url)
                else:
                    break
            else:
                break
        
        # 자기 자신 링크 등 제외하고, 최신 항목(HTML 상단)이 나중에 DB에 들어가도록 순서를 뒤집음
        items_to_process = all_items
        items_to_process.reverse()
        
        if not items_to_process:
            return result
        
        for detail_url, list_title, period_text in items_to_process:
            if detail_url in seen:
                continue
                
            title = list_title
            
            # 2. 목록 페이지에서 제목 추출 실패 시 상세 페이지 방문
            if title == "공지" or not title:
                detail_html = await fetch_html(detail_url)
                if not detail_html:
                    continue
                title = _extract_detail_title(detail_html, title_selector)
                
            if not title:
                title = "공지"

            start_dt, end_dt = parse_event_period(period_text)

            notice = Notice(
                airline_id=airline_id,
                source_url=detail_url,
                content_type="text",
                raw_content=title,
                extracted_text=title,
                is_special_deal=False,
                event_start=start_dt,
                event_end=end_dt,
            )
            session.add(notice)
            await session.flush()
            result.append((airline_id, airline_name, detail_url, "text", title))
            seen.add(detail_url)
            
        return result
