from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.user import User
from app.repositories.base import BaseRepo


class UserRepo(BaseRepo):
    async def get_by_tg_id(self, tg_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.tg_id == tg_id))
        return result.scalar_one_or_none()

    async def upsert(self, tg_id: int, username: str | None, lang: str | None) -> User:
        stmt = (
            pg_insert(User)
            .values(tg_id=tg_id, username=username, lang=lang)
            .on_conflict_do_update(
                index_elements=["tg_id"],
                set_={"username": username, "lang": lang},
            )
            .returning(User)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def count(self) -> int:
        result = await self.session.execute(select(User.id))
        return len(result.scalars().all())
