from datetime import datetime
from typing import Any, List

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.features.connections.models import (
    Connection,
    ConnectionCreate,
    ConnectionStatus,
    ConnectionUpdate,
)
from app.features.users.models import User


async def create_connection(
    *, session: AsyncSession, connection_create: ConnectionCreate, source_user: User
) -> Connection:
    # Check if connection already exists
    existing_connection = await get_connection_by_users(
        session=session,
        source_user_id=source_user.id,
        target_user_id=connection_create.target_user_id,
    )
    if existing_connection:
        return existing_connection

    connection = Connection(
        source_user_id=source_user.id,
        target_user_id=connection_create.target_user_id,
        status=connection_create.status,
    )
    session.add(connection)
    await session.commit()
    await session.refresh(connection)
    return connection


async def update_connection(
    *, session: AsyncSession, connection: Connection, connection_update: ConnectionUpdate
) -> Connection:
    connection_data = connection_update.model_dump(exclude_unset=True)
    connection_data["updated_at"] = datetime.utcnow()
    connection.sqlmodel_update(connection_data)
    session.add(connection)
    await session.commit()
    await session.refresh(connection)
    return connection


async def get_connection(
    *, session: AsyncSession, connection_id: str
) -> Connection | None:
    statement = select(Connection).where(Connection.id == connection_id)
    result = await session.exec(statement)
    return result.first()


async def get_connection_by_users(
    *, session: AsyncSession, source_user_id: str, target_user_id: str
) -> Connection | None:
    statement = select(Connection).where(
        Connection.source_user_id == source_user_id,
        Connection.target_user_id == target_user_id,
    )
    result = await session.exec(statement)
    return result.first()


async def get_user_connections(
    *, session: AsyncSession, user_id: str, status: ConnectionStatus | None = None
) -> List[Connection]:
    statement = select(Connection).where(
        (Connection.source_user_id == user_id) | (Connection.target_user_id == user_id)
    )
    if status:
        statement = statement.where(Connection.status == status)
    result = await session.exec(statement)
    return result.all()


async def delete_connection(*, session: AsyncSession, connection: Connection) -> None:
    await session.delete(connection)
    await session.commit() 