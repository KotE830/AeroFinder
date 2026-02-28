from datetime import datetime
from pydantic import BaseModel


class MonitorUrlCreate(BaseModel):
    url: str
    list_link_selector: str  # 목록 페이지에서 이벤트(상세) 링크 선택자
    detail_title_selector: str  # 상세 페이지에서 제목 선택자
    list_period_selector: str | None = None  # 목록 페이지에서 기간 선택자
    list_next_selector: str | None = None  # 다음 페이지 버튼 선택자


class MonitorUrlUpdate(BaseModel):
    list_link_selector: str | None = None
    detail_title_selector: str | None = None
    list_period_selector: str | None = None
    list_next_selector: str | None = None


class MonitorUrlResponse(BaseModel):
    id: str
    airline_id: str
    url: str
    last_checked_at: datetime | None = None
    list_link_selector: str | None = None
    detail_title_selector: str | None = None
    list_period_selector: str | None = None
    list_next_selector: str | None = None

    model_config = {"from_attributes": True}
