"""
항공사 CRUD (URL은 monitor_urls로 별도 등록)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.db_models import Airline, MonitorUrl
from app.schemas.airline import AirlineCreate, AirlineUpdate, AirlineResponse
from app.schemas.monitor_url import MonitorUrlCreate, MonitorUrlResponse, MonitorUrlUpdate

router = APIRouter()


@router.get("", response_model=list[AirlineResponse])
async def list_airlines(db: AsyncSession = Depends(get_db)):
    q = select(Airline).order_by(Airline.name)
    res = await db.execute(q)
    return res.scalars().all()


@router.post("", response_model=AirlineResponse)
async def create_airline(body: AirlineCreate, db: AsyncSession = Depends(get_db)):
    airline = Airline(
        name=body.name,
        base_url=body.base_url,
        logo_url=body.logo_url,
    )
    db.add(airline)
    await db.flush()
    await db.refresh(airline)
    return airline


@router.get("/{airline_id}", response_model=AirlineResponse)
async def get_airline(airline_id: str, db: AsyncSession = Depends(get_db)):
    q = select(Airline).where(Airline.id == airline_id)
    res = await db.execute(q)
    row = res.scalar_one_or_none()
    if not row:
        raise HTTPException(404, "Airline not found")
    return row


@router.patch("/{airline_id}", response_model=AirlineResponse)
async def update_airline(airline_id: str, body: AirlineUpdate, db: AsyncSession = Depends(get_db)):
    q = select(Airline).where(Airline.id == airline_id)
    res = await db.execute(q)
    airline = res.scalar_one_or_none()
    if not airline:
        raise HTTPException(404, "Airline not found")
    if body.name is not None:
        airline.name = body.name
    if body.base_url is not None:
        airline.base_url = body.base_url
    if body.logo_url is not None:
        airline.logo_url = body.logo_url
    await db.flush()
    await db.refresh(airline)
    return airline


@router.delete("/{airline_id}", status_code=204)
async def delete_airline(airline_id: str, db: AsyncSession = Depends(get_db)):
    q = select(Airline).where(Airline.id == airline_id)
    res = await db.execute(q)
    airline = res.scalar_one_or_none()
    if not airline:
        raise HTTPException(404, "Airline not found")
    await db.delete(airline)
    return None


# Monitor URLs (감시할 공지 URL)
@router.get("/{airline_id}/urls", response_model=list[MonitorUrlResponse])
async def list_monitor_urls(airline_id: str, db: AsyncSession = Depends(get_db)):
    q = select(MonitorUrl).where(MonitorUrl.airline_id == airline_id)
    res = await db.execute(q)
    return res.scalars().all()


@router.post("/{airline_id}/urls", response_model=MonitorUrlResponse)
async def add_monitor_url(airline_id: str, body: MonitorUrlCreate, db: AsyncSession = Depends(get_db)):
    q = select(Airline).where(Airline.id == airline_id)
    res = await db.execute(q)
    if res.scalar_one_or_none() is None:
        raise HTTPException(404, "Airline not found")
    mu = MonitorUrl(
        airline_id=airline_id,
        url=body.url,
        list_link_selector=body.list_link_selector,
        detail_title_selector=body.detail_title_selector,
        list_period_selector=body.list_period_selector,
        list_next_selector=body.list_next_selector,
    )
    db.add(mu)
    await db.flush()
    await db.refresh(mu)
    return mu


@router.patch("/{airline_id}/urls/{url_id}", response_model=MonitorUrlResponse)
async def update_monitor_url(
    airline_id: str,
    url_id: str,
    body: MonitorUrlUpdate,
    db: AsyncSession = Depends(get_db),
):
    q = select(MonitorUrl).where(MonitorUrl.id == url_id, MonitorUrl.airline_id == airline_id)
    res = await db.execute(q)
    row = res.scalar_one_or_none()
    if not row:
        raise HTTPException(404, "Monitor URL not found")
    if body.list_link_selector is not None:
        row.list_link_selector = body.list_link_selector
    if body.detail_title_selector is not None:
        row.detail_title_selector = body.detail_title_selector
    if body.list_period_selector is not None:
        row.list_period_selector = body.list_period_selector
    if body.list_next_selector is not None:
        row.list_next_selector = body.list_next_selector
    await db.flush()
    await db.refresh(row)
    return row


@router.delete("/{airline_id}/urls/{url_id}", status_code=204)
async def delete_monitor_url(airline_id: str, url_id: str, db: AsyncSession = Depends(get_db)):
    q = select(MonitorUrl).where(MonitorUrl.id == url_id, MonitorUrl.airline_id == airline_id)
    res = await db.execute(q)
    row = res.scalar_one_or_none()
    if not row:
        raise HTTPException(404, "Monitor URL not found")
    await db.delete(row)
    return None


@router.delete("/{airline_id}/data", status_code=204)
async def delete_crawled_data(airline_id: str, db: AsyncSession = Depends(get_db)):
    """Clear all crawled Deals, Notices, and reset MonitorUrl hashes for a specific airline."""
    from app.models.db_models import Notice, Deal
    from sqlalchemy import delete, update
    
    # Verify airline exists
    q = select(Airline).where(Airline.id == airline_id)
    res = await db.execute(q)
    if not res.scalar_one_or_none():
        raise HTTPException(404, "Airline not found")
        
    # Delete Deals
    await db.execute(delete(Deal).where(Deal.airline_id == airline_id))
    
    # Delete Notices
    await db.execute(delete(Notice).where(Notice.airline_id == airline_id))
    
    # Reset MonitorUrl hashes
    await db.execute(
        update(MonitorUrl)
        .where(MonitorUrl.airline_id == airline_id)
        .values(last_html_hash=None, last_checked_at=None)
    )
    
    await db.commit()
    return None
