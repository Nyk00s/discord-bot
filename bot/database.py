import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import aiosqlite


engine = create_async_engine(os.getenv("DB_URL"), echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession,
    expire_on_commit=False
)
