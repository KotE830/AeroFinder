"""
크롤링된 전체 공지 API (이벤트만이 아닌 모든 공지)
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.models.db_models import Notice
from app.models.notice import NoticeResponse

router = APIRouter()


def _notice_title(notice: Notice, airline_name: str) -> str:
    """공지 제목: extracted_text 앞 100자. 항공사명과 같으면 URL 경로로 대체."""
    from urllib.parse import urlparse

    def _path_fallback() -> str:
        parsed = urlparse(notice.source_url or "")
        path = (parsed.path or "").strip("/")
        if path:
            parts = path.split("/")
            return parts[-1] or path
        return "공지"

    if notice.extracted_text and notice.extracted_text.strip():
        s = notice.extracted_text.strip().replace("\n", " ")[:100]
        out = s + ("..." if len(notice.extracted_text.strip()) > 100 else "")
        if out != "공지" and out.strip() != (airline_name or "").strip():
            return out
    return _path_fallback()


@router.get("", response_model=list[NoticeResponse])
async def get_notices(
    db: AsyncSession = Depends(get_db),
    airline_id: str | None = Query(None, description="특정 항공사만"),
    is_special_deal: bool | None = Query(None, description="특가만"),
):
    """앱에서 조회: 크롤링된 공지 목록. airline_id / is_special_deal 로 필터 가능."""
    try:
        q = (
            select(Notice)
            .options(selectinload(Notice.airline))
            .order_by(Notice.created_at.desc())
        )
        if airline_id is not None and airline_id.strip():
            q = q.where(Notice.airline_id == airline_id.strip())
        if is_special_deal is True:
            q = q.where(Notice.is_special_deal == True)  # noqa: E712
        res = await db.execute(q)
        notices = res.scalars().all()
        return [
            NoticeResponse(
                id=n.id,
                airline=n.airline.name,
                source_url=n.source_url,
                title=_notice_title(n, n.airline.name if n.airline else ""),
                content_type=n.content_type,
                event_start=n.event_start,
                event_end=n.event_end,
                is_special_deal=n.is_special_deal,
                created_at=n.created_at,
            )
            for n in notices
        ]
    except SQLAlchemyError:
        return []

from pydantic import BaseModel

class ToggleDealRequest(BaseModel):
    is_special_deal: bool

@router.put("/{notice_id}/toggle_deal")
async def toggle_notice_special_deal(
    notice_id: str,
    req: ToggleDealRequest,
    db: AsyncSession = Depends(get_db)
):
    """지정된 공지를 수동으로 특가로 강제 설정하거나, 특가에서 제외합니다."""
    notice = await db.get(Notice, notice_id)
    if not notice:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="해당 공지를 찾을 수 없습니다.")
        
    notice.is_special_deal = req.is_special_deal
    if req.is_special_deal:
        from app.models.db_models import Deal
        existing = await db.execute(select(Deal).where(Deal.notice_id == notice_id))
        if not existing.scalar_one_or_none():
            from app.services.analyzer import push_notice_to_deal
            await push_notice_to_deal(db, notice)
    else:
        from app.models.db_models import Deal
        deals = await db.execute(select(Deal).where(Deal.notice_id == notice_id))
        for d in deals.scalars().all():
            await db.delete(d)
            
    await db.commit()
    return {"status": "ok", "is_special_deal": notice.is_special_deal}
