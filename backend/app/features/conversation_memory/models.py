import uuid
from datetime import datetime
from typing_extensions import Self

from letta_client.types.letta_message_union import LettaMessageUnion
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
class ChatConversationInfo(BaseModel):
    conversation_id: str
    name: str


class ChatConversationsResponse(BaseModel):
    conversations_info: list[ChatConversationInfo]


class ChatConversationCreationResponse(BaseModel):
    conversation_id: str


class ChatMessageRequest(BaseModel):
    message: str


class ChatMessage(BaseModel):
    content: str
    message_type: str

    @classmethod
    def from_message_union(cls, message: LettaMessageUnion) -> Self:
        return cls(content=message.content, message_type=message.message_type)


class ChatMessageResponse(BaseModel):
    messages: list[ChatMessage]


class ChatHistoryResponse(BaseModel):
    messages: list[ChatMessage]
