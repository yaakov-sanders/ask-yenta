from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.core.db import with_async_session
from app.features.connections.connections_models import Connection, ConnectionStatus


@with_async_session
async def validate_connections(
    current_user_id: str, other_user_ids: list[str], session: AsyncSession
):
    query = select(Connection).where(
        (
            (
                (Connection.source_user_id == current_user_id)
                & Connection.target_user_id.in_(other_user_ids)
            )
            | (
                (Connection.target_user_id == current_user_id)
                & Connection.source_user_id.in_(other_user_ids)
            )
        )
        & (Connection.status == ConnectionStatus.ACCEPTED)
    )
    res = await session.exec(query)
    connections: list[Connection] = res.all()
    connected_user_ids = {str(c.source_user_id) for c in connections} | {
        str(c.target_user_id) for c in connections
    }
    non_connected_user_ids = []
    for user_id in other_user_ids:
        if user_id not in connected_user_ids:
            non_connected_user_ids.append(user_id)

    if non_connected_user_ids:
        raise HTTPException(
            422, f"Users {non_connected_user_ids} are not connected to current user"
        )
