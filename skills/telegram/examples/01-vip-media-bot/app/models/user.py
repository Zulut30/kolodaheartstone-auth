from enum import StrEnum

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Role(StrEnum):
    user = "user"
    admin = "admin"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None]
    lang: Mapped[str | None]
    role: Mapped[Role] = mapped_column(default=Role.user)
    is_banned: Mapped[bool] = mapped_column(default=False)
