import uuid
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import JSON, Column, Text
from sqlmodel import Field, SQLModel


class ConversationMemory(SQLModel, table=True):
    __tablename__ = "conversation_memory"

    user_id: uuid.UUID = Field(primary_key=True)
    summary: str = Field(default="", sa_column=Column(Text))
    messages: list[dict[str, str]] = Field(default=[], sa_column=Column(JSON))
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# API schemas
class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    updated_summary: str
