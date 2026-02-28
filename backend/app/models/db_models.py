"""
PostgreSQL 테이블 모델
"""
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def gen_uuid():
    return str(uuid4())


class Airline(Base):
    __tablename__ = "airlines"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    base_url: Mapped[str] = mapped_column(Text, nullable=False)
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    monitor_urls: Mapped[list["MonitorUrl"]] = relationship(back_populates="airline", cascade="all, delete-orphan")
    keywords: Mapped[list["Keyword"]] = relationship(back_populates="airline", cascade="all, delete-orphan")
    notices: Mapped[list["Notice"]] = relationship(back_populates="airline", cascade="all, delete-orphan")
    deals: Mapped[list["Deal"]] = relationship(back_populates="airline", cascade="all, delete-orphan")


class Keyword(Base):
    """특가 판별용 키워드. airline_id 가 NULL 이면 공통 키워드(모든 항공사 적용)."""
    __tablename__ = "keywords"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=gen_uuid)
    airline_id: Mapped[str | None] = mapped_column(Text, ForeignKey("airlines.id", ondelete="CASCADE"), nullable=True)  # None = 공통
    keyword: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    airline: Mapped["Airline | None"] = relationship("Airline", back_populates="keywords")


class MonitorUrl(Base):
    """감시할 공지 URL. list_link_selector 있으면 목록→상세 링크 크롤링, 없으면 단일 페이지 hash 비교."""
    __tablename__ = "monitor_urls"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=gen_uuid)
    airline_id: Mapped[str] = mapped_column(Text, ForeignKey("airlines.id", ondelete="CASCADE"), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    last_html_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    list_link_selector: Mapped[str | None] = mapped_column(Text, nullable=True)  # 목록 페이지에서 이벤트(상세) 링크 선택자
    detail_title_selector: Mapped[str | None] = mapped_column(Text, nullable=True)  # 상세 페이지에서 제목 선택자 (없으면 title/og:title/h1)
    list_period_selector: Mapped[str | None] = mapped_column(Text, nullable=True)  # 목록 페이지에서 기간 텍스트 선택자
    list_next_selector: Mapped[str | None] = mapped_column(Text, nullable=True)  # 다음 페이지 버튼 선택자

    airline: Mapped["Airline"] = relationship("Airline", back_populates="monitor_urls")


class Notice(Base):
    """감지된 공지 (hash 변경 시 생성). 분석 후 특가면 Deal로 푸시."""
    __tablename__ = "notices"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=gen_uuid)
    airline_id: Mapped[str] = mapped_column(Text, ForeignKey("airlines.id", ondelete="CASCADE"), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(Text, nullable=False)  # "text" | "image"
    raw_content: Mapped[str | None] = mapped_column(Text, nullable=True)  # HTML 조각 또는 이미지 URL/base64
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    event_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    routes: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True)
    is_special_deal: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    analyzed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    airline: Mapped["Airline"] = relationship("Airline", back_populates="notices")


class Deal(Base):
    """앱에 푸시되는 특가 정보. 오픈 후 가격 크롤러가 price를 채울 수 있음."""
    __tablename__ = "deals"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=gen_uuid)
    notice_id: Mapped[str | None] = mapped_column(Text, ForeignKey("notices.id", ondelete="SET NULL"), nullable=True)
    airline_id: Mapped[str] = mapped_column(Text, ForeignKey("airlines.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    event_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    event_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    routes: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True)  # e.g. ["ICN-GMP", "GMP-CJU"]
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 0), nullable=True)  # 오픈 후 크롤러가 채움
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    airline: Mapped["Airline"] = relationship("Airline", back_populates="deals")
