from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import engine
from app.features.users.users_models import User


async def convert_identity_ids_to_user_ids(identity_ids: list[str]) -> dict[str, str]:
    async with AsyncSession(engine) as session:
        query = select(User).where(User.identity_id.in_(identity_ids))
        res = await session.exec(query)
        users: list[User] = res.all()
        return {u.identity_id: str(u.id) for u in users}
