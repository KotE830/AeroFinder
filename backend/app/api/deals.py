"""
항공사 특가·이벤트 API (DB 연동)
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.models.db_models import Deal, Airline
from app.models.deal import DealResponse

router = APIRouter()


@router.get("", response_model=list[DealResponse])
async def get_deals(db: AsyncSession = Depends(get_db)):
    """앱에서 조회: 국내 항공사 특가 이벤트 목록 (항공사명 포함)."""
    try:
        q = (
            select(Deal)
            .options(selectinload(Deal.airline))
            .join(Deal.airline)
            .order_by(
                Deal.event_start.desc().nulls_last(),
                Deal.event_end.desc().nulls_last(),
                Airline.name.asc()
            )
        )
        res = await db.execute(q)
        deals = res.scalars().all()
        return [
            DealResponse(
                id=d.id,
                airline=d.airline.name,
                airline_id=d.airline_id,
                title=d.title,
                description=d.description,
                url=d.url,
                image_url=d.image_url,
                event_start=d.event_start,
                event_end=d.event_end,
                routes=d.routes,
                price=d.price,
                created_at=d.created_at,
            )
            for d in deals
        ]
    except SQLAlchemyError:
        return []
