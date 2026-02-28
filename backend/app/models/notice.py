"""
크롤링된 공지 응답 모델 (API)
"""
from datetime import datetime
from pydantic import BaseModel


class NoticeResponse(BaseModel):
    """공지 한 건 (전체 공지 탭용)"""

    id: str
    airline: str
    source_url: str
    title: str
    content_type: str
    event_start: datetime | None = None
    event_end: datetime | None = None
    is_special_deal: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}
