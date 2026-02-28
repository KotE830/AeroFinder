"""
항공 특가·이벤트 응답 모델 (API)
"""
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class DealResponse(BaseModel):
    """특가 이벤트 한 건 (앱 푸시용)"""

    id: str
    airline: str
    airline_id: str
    title: str
    description: str | None = None
    url: str
    image_url: str | None = None
    event_start: datetime | None = None
    event_end: datetime | None = None
    routes: list | dict | None = None
    price: Decimal | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
