from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

import app.features.users.users_crud
from app.core.config import settings
from app.features.users.users_models import User, UserCreate

# Convert database URI to async format (replace postgresql:// with postgresql+asyncpg://)
database_uri = str(settings.SQLALCHEMY_DATABASE_URI)
if database_uri.startswith("postgresql://"):
    database_uri = database_uri.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
engine = create_async_engine(database_uri)


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


async def init_db(session: AsyncSession) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel
    # async with engine.begin() as conn:
    #     await conn.run_sync(SQLModel.metadata.create_all)

    statement = select(User).where(User.email == settings.FIRST_SUPERUSER)
    result = await session.exec(statement)
    user = result.first()

    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name=settings.FIRST_SUPERUSER_NAME,
            is_superuser=True,
        )
        await app.features.users.crud.create_user(session=session, user_create=user_in)


async def save_to_db(model: SQLModel):
    async with AsyncSession(engine) as session:
        session.add(model)
        await session.commit()
        await session.refresh(model)
