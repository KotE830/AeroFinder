from pydantic import BaseModel


class KeywordCreate(BaseModel):
    keyword: str
    airline_id: str | None = None  # None = 공통 키워드


class KeywordResponse(BaseModel):
    id: str
    keyword: str
    airline_id: str | None = None

    model_config = {"from_attributes": True}
