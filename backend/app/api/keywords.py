"""
키워드 CRUD (특가 판별용. airline_id 없으면 공통 키워드)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.db_models import Keyword
from app.schemas.keyword import KeywordCreate, KeywordResponse

router = APIRouter()


@router.get("", response_model=list[KeywordResponse])
async def list_keywords(airline_id: str | None = None, db: AsyncSession = Depends(get_db)):
    q = select(Keyword)
    if airline_id is not None:
        q = q.where((Keyword.airline_id == airline_id) | (Keyword.airline_id.is_(None)))
    res = await db.execute(q)
    return res.scalars().all()


@router.post("", response_model=KeywordResponse)
async def create_keyword(body: KeywordCreate, db: AsyncSession = Depends(get_db)):
    kw = Keyword(keyword=body.keyword, airline_id=body.airline_id)
    db.add(kw)
    await db.flush()
    await db.refresh(kw)
    return kw


@router.delete("/{keyword_id}", status_code=204)
async def delete_keyword(keyword_id: str, db: AsyncSession = Depends(get_db)):
    q = select(Keyword).where(Keyword.id == keyword_id)
    res = await db.execute(q)
    row = res.scalar_one_or_none()
    if not row:
        raise HTTPException(404, "Keyword not found")
    await db.delete(row)
    return None
