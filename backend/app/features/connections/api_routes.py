from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.features.core.api_deps import get_current_user, get_db
from app.features.connections import crud, models
from app.features.users.models import User

router = APIRouter()


@router.post("/", response_model=models.ConnectionPublic)
async def create_connection(
    *,
    session: AsyncSession = Depends(get_db),
    connection_in: models.ConnectionCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new connection request.
    """
    connection = await crud.create_connection(
        session=session, connection_create=connection_in, source_user=current_user
    )
    return connection


@router.get("/", response_model=models.ConnectionsPublic)
async def read_connections(
    *,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: models.ConnectionStatus | None = None,
    skip: int = 0,
    limit: int = Query(default=100, le=100),
) -> Any:
    """
    Retrieve connections.
    """
    connections = await crud.get_user_connections(
        session=session, user_id=str(current_user.id), status=status
    )
    return {"data": connections, "count": len(connections)}


@router.get("/{connection_id}", response_model=models.ConnectionPublic)
async def read_connection(
    *,
    session: AsyncSession = Depends(get_db),
    connection_id: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get connection by ID.
    """
    connection = await crud.get_connection(session=session, connection_id=connection_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    if str(connection.source_user_id) != str(current_user.id) and str(
        connection.target_user_id
    ) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return connection


@router.put("/{connection_id}", response_model=models.ConnectionPublic)
async def update_connection(
    *,
    session: AsyncSession = Depends(get_db),
    connection_id: str,
    connection_in: models.ConnectionUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update a connection.
    """
    connection = await crud.get_connection(session=session, connection_id=connection_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    if str(connection.target_user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    connection = await crud.update_connection(
        session=session, connection=connection, connection_update=connection_in
    )
    return connection


@router.delete("/{connection_id}")
async def delete_connection(
    *,
    session: AsyncSession = Depends(get_db),
    connection_id: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Delete a connection.
    """
    connection = await crud.get_connection(session=session, connection_id=connection_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    if str(connection.source_user_id) != str(current_user.id) and str(
        connection.target_user_id
    ) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await crud.delete_connection(session=session, connection=connection)
    return {"ok": True} 