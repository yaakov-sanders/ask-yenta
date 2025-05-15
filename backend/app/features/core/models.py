import uuid

from sqlmodel import SQLModel


class Message(SQLModel):
    message: str


class TokenPayload(SQLModel):
    sub: uuid.UUID | None = None
