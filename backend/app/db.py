"""
PostgreSQL 연결 및 세션
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """테이블 생성 (앱 시작 시 호출) + 기존 DB에 logo_url 등 누락 컬럼 추가"""
    from app.models import db_models  # noqa: F401 - register tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # 기존 airlines 테이블에 logo_url 없으면 추가 (create_all은 기존 테이블 수정 안 함)
    async with engine.begin() as conn:
        await conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = 'airlines' AND column_name = 'logo_url'
                ) THEN
                    ALTER TABLE airlines ADD COLUMN logo_url TEXT;
                END IF;
            END $$
        """))
        await conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = 'monitor_urls' AND column_name = 'list_link_selector'
                ) THEN
                    ALTER TABLE monitor_urls ADD COLUMN list_link_selector TEXT;
                END IF;
            END $$
        """))
        await conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = 'monitor_urls' AND column_name = 'detail_title_selector'
                ) THEN
                    ALTER TABLE monitor_urls ADD COLUMN detail_title_selector TEXT;
                END IF;
            END $$
        """))
        await conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = 'monitor_urls' AND column_name = 'list_period_selector'
                ) THEN
                    ALTER TABLE monitor_urls ADD COLUMN list_period_selector TEXT;
                END IF;
            END $$
        """))
        await conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = 'airlines' AND column_name = 'crawler_slug'
                ) THEN
                    ALTER TABLE airlines ADD COLUMN crawler_slug TEXT;
                END IF;
            END $$
        """))
        await conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = 'monitor_urls' AND column_name = 'list_next_selector'
                ) THEN
                    ALTER TABLE monitor_urls ADD COLUMN list_next_selector TEXT;
                END IF;
            END $$
        """))