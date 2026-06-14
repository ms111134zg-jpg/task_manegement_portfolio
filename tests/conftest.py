import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict
from backend.app.main import app
from backend.app.db import get_db
from backend.app.models.base import Base
from sqlalchemy.pool import NullPool

class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.test",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    POSTGRE_HOST: str
    POSTGRE_PORT: int
    POSTGRE_DB: str
    POSTGRE_USER: str
    POSTGRE_PW: str

test_settings = TestSettings()

TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{test_settings.POSTGRE_USER}:{test_settings.POSTGRE_PW}"
    f"@{test_settings.POSTGRE_HOST}:{test_settings.POSTGRE_PORT}/{test_settings.POSTGRE_DB}"
)

engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True, scope="function")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac