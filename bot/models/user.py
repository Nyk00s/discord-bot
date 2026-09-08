from .base import Base
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    discord_id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    user_name: Mapped[str] = mapped_column(nullable=False)
    points: Mapped[int] = mapped_column(nullable=False, default=0)
    randomizer_date: Mapped[datetime] = mapped_column(nullable=True)
