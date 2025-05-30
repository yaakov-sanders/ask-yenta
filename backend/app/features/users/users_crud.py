import asyncio
from typing import Any

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import with_async_session
from app.core.security import get_password_hash
from app.features.letta_logic.letta_logic import create_block
from app.features.prompts.yenta_persona import yenta_persona_prompt
from app.features.users.users_models import User, UserCreate, UserUpdate


async def create_letta_fields(user: User):
    yenta_block, profile_block = await asyncio.gather(
        create_block("persona", yenta_persona_prompt),
        create_block("human", f"Profile: {user.full_name}"),
    )

    user.profile_block_id, user.yenta_block_id = (
        profile_block.id,
        yenta_block.id,
    )


async def create_user(*, session: AsyncSession, user_create: UserCreate) -> User:
    user = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    await create_letta_fields(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(
    *, session: AsyncSession, db_user: User, user_in: UserUpdate
) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def get_user_by_email(*, session: AsyncSession, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    result = await session.exec(statement)
    return result.first()


@with_async_session
async def get_users_by_ids(user_ids: list[str], session: AsyncSession) -> list[User]:
    statement = select(User).where(User.id.in_(user_ids))
    result = await session.exec(statement)
    return result.all()
