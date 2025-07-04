from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.features.connections.connections_crud import (
    get_user_connections,
    get_connection,
    create_connection,
    update_connection,
    delete_connection,
)
from app.features.connections.connections_models import (
    ConnectionPublic,
    ConnectionCreate,
    ConnectionsPublic,
    ConnectionStatus,
    ConnectionUpdate,
)
from app.features.core.api_deps import get_current_user, get_db
from app.features.users.users_models import User

router = APIRouter(prefix="/connections", tags=["connections"])


@router.post("/", response_model=ConnectionPublic)
async def create_connection_endpoint(
    *,
    session: AsyncSession = Depends(get_db),
    connection_in: ConnectionCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new connection request.
    """
    connection = await create_connection(
        session=session, connection_create=connection_in, source_user=current_user
    )
    return connection


@router.get("/", response_model=ConnectionsPublic)
async def read_connections(
    *,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: ConnectionStatus | None = None,
    skip: int = 0,
    limit: int = Query(default=100, le=100),
) -> Any:
    """
    Retrieve connections.
    """
    connections = await get_user_connections(
        session=session, user_id=str(current_user.id), status=status
    )
    return {"data": connections, "count": len(connections)}


@router.get("/{connection_id}", response_model=ConnectionPublic)
async def read_connection(
    *,
    session: AsyncSession = Depends(get_db),
    connection_id: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get connection by ID.
    """
    connection = await get_connection(session=session, connection_id=connection_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    if str(connection.source_user_id) != str(current_user.id) and str(
        connection.target_user_id
    ) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return connection


@router.put("/{connection_id}", response_model=ConnectionPublic)
async def update_connection_endpoint(
    *,
    session: AsyncSession = Depends(get_db),
    connection_id: str,
    connection_in: ConnectionUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update a connection.
    """
    connection = await get_connection(session=session, connection_id=connection_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    if str(connection.target_user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    connection = await update_connection(
        session=session, connection=connection, connection_update=connection_in
    )
    return connection


@router.delete("/{connection_id}")
async def delete_connection_endpoint(
    *,
    session: AsyncSession = Depends(get_db),
    connection_id: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Delete a connection.
    """
    connection = await get_connection(session=session, connection_id=connection_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    if str(connection.source_user_id) != str(current_user.id) and str(
        connection.target_user_id
    ) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await delete_connection(session=session, connection=connection)
    return {"ok": True}
