from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .settings import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # 開発中はTrueでもOK（SQLログが出る）
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try :
            yield session
        
        except Exception:
            await session.rollback()
            raise

