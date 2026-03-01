"""
관리: 파이프라인 수동 실행, 가격 크롤링, 사이트 정보 조회 등
"""
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.db import get_db
from app.services.pipeline import run_pipeline
from app.services.price_crawler import update_deal_prices
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/site-info")
async def get_site_info(url: str):
    """URL 페이지에서 title, favicon/og:image 추출 (항공사 추가 시 이름·로고 자동 채우기용)."""
    if not url.strip().startswith(("http://", "https://")):
        raise HTTPException(400, "Invalid URL")
    timeout = getattr(settings, "http_timeout_seconds", 30.0)
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
            r = await client.get(url)
            r.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(502, f"Failed to fetch URL: {e!s}")
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    soup = BeautifulSoup(r.text, "html.parser")
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    if not title and soup.find("meta", property="og:title"):
        title = (soup.find("meta", property="og:title") or {}).get("content", "").strip()
    logo_url: str | None = None
    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        logo_url = urljoin(origin, og_image["content"].strip())
    if not logo_url:
        favicon = soup.find("link", rel=lambda x: x and "icon" in x.lower() if x else False)
        if favicon and favicon.get("href"):
            logo_url = urljoin(origin, favicon["href"].strip())
    if not logo_url:
        logo_url = urljoin(origin, "/favicon.ico")
    if not title:
        title = parsed.netloc or "항공사"
    return {"name": title, "logo_url": logo_url}


@router.post("/crawl")
async def trigger_crawl():
    """공지 감지 → 분석 → 푸시 파이프라인 수동 1회 실행."""
    await run_pipeline()
    return {"status": "ok", "message": "pipeline run once"}


@router.delete("/clear-data")
async def clear_crawled_data(db: AsyncSession = Depends(get_db)):
    """수집된 모든 공지(Notices)와 특가(Deals) 데이터를 초기화합니다."""
    from sqlalchemy import delete, update
    from app.models.db_models import Notice, Deal, MonitorUrl
    try:
        # Delete crawled data
        await db.execute(delete(Deal))
        await db.execute(delete(Notice))
        
        # Reset monitor urls so it triggers a fresh crawl next time
        await db.execute(update(MonitorUrl).values(last_checked_at=None, last_html_hash=None))
        
        await db.commit()
        return {"status": "ok", "message": "All crawled data (Notices, Deals) has been cleared."}
    except Exception as e:
        await db.rollback()
        raise HTTPException(500, f"Failed to clear data: {e!s}")

@router.post("/price-update")
async def trigger_price_update(
    deal_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """price가 비어 있는 Deal에 대해 URL에서 가격 크롤링 후 저장."""
    updated = await update_deal_prices(db, deal_id=deal_id)
    return {"status": "ok", "updated_count": updated}


class SubscribeRequest(BaseModel):
    token: str
    topic: str = "all_users"

@router.post("/subscribe")
async def subscribe_topic(req: SubscribeRequest):
    """클라이언트 기기 토큰을 특정 튜픽(all_users)에 구독."""
    try:
        import firebase_admin
        from firebase_admin import messaging
        try:
            firebase_admin.get_app()
        except ValueError:
            raise HTTPException(status_code=500, detail="Firebase Admin SDK is not initialized.")
            
        response = messaging.subscribe_to_topic([req.token], req.topic)
        if response.failure_count > 0:
            raise HTTPException(status_code=400, detail=response.errors[0].reason)
        return {"status": "ok", "message": f"Subscribed to {req.topic}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to subscribe: {str(e)}")

class PushNotificationRequest(BaseModel):
    title: str
    body: str
    topic: str = "all_users"

@router.post("/push")
async def send_push_notification(req: PushNotificationRequest):
    """관리자가 수동으로 FCM 푸시 알림 발송."""
    try:
        import firebase_admin
        from firebase_admin import messaging
        
        # Check if default app exists
        try:
            firebase_admin.get_app()
        except ValueError:
            raise HTTPException(status_code=500, detail="Firebase Admin SDK is not initialized.")

        message = messaging.Message(
            notification=messaging.Notification(
                title=req.title,
                body=req.body,
            ),
            topic=req.topic,
        )
        response = messaging.send(message)
        return {"status": "ok", "message_id": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to send push notification: {str(e)}")
