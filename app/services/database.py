from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.settings import SETTINGS


DATABASE_URL = f"postgresql+asyncpg://{SETTINGS.DB_USER.get_secret_value()}:{SETTINGS.DB_PASS.get_secret_value()}@{SETTINGS.DB_HOST}:{SETTINGS.DB_PORT}/{SETTINGS.DB_NAME.get_secret_value()}"

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
