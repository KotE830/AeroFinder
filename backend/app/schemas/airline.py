from pydantic import BaseModel


class AirlineCreate(BaseModel):
    name: str
    base_url: str
    logo_url: str | None = None


class AirlineUpdate(BaseModel):
    name: str | None = None
    base_url: str | None = None
    logo_url: str | None = None


class AirlineResponse(BaseModel):
    id: str
    name: str
    base_url: str
    logo_url: str | None = None

    model_config = {"from_attributes": True}
