import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel
from sqlmodel import Field, SQLModel

if TYPE_CHECKING:
    pass


class ConnectionStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


# Shared properties
class ConnectionBase(SQLModel):
    status: ConnectionStatus = Field(default=ConnectionStatus.PENDING)


# Properties to receive via API on creation
class ConnectionCreate(ConnectionBase):
    target_user_id: uuid.UUID


# Properties to receive via API on update
class ConnectionUpdate(ConnectionBase):
    pass


# Database model
class Connection(ConnectionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    source_user_id: uuid.UUID = Field(foreign_key="user.id")
    target_user_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Properties to return via API
class ConnectionPublic(ConnectionBase):
    id: uuid.UUID
    source_user_id: uuid.UUID
    target_user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ConnectionsPublic(SQLModel):
    data: list[ConnectionPublic]
    count: int 