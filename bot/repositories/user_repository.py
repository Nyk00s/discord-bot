from sqlalchemy.ext.asyncio import AsyncSession
from bot.models import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker


class UserRepository:

    def __init__(self, session_factory: async_sessionmaker[AsyncSession] ):
        self.session_factory = session_factory

    async def  get_user(self, id: int) -> User:
        async with self.session_factory() as session:
            stmt = select(User).where(User.discord_id == id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_by_points(self, limit: int, desc=True) -> list[User]:
        async with self.session_factory() as session:
            stmt = select(User).order_by(User.points.desc()).limit(limit)
            result = await session.execute(stmt)
            return list(result.all())

    async def create_user_or_get(self, user_id, username) -> User:
        async with self.session_factory() as session:
            user = await self.get_user(user_id)
            if not user:
                user = User(discord_id=user_id, user_name=username)
                session.add(user)
                await session.commit()
                await session.refresh(user)
            return user

    async def update(self, user: User) -> User:
        async with self.session_factory() as session:
            user = await session.merge(user)
            await session.commit()
            await session.refresh(user)
            return user
