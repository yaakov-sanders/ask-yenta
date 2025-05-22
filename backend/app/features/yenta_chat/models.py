import uuid
from datetime import datetime
from typing import Literal

from letta_client.types.assistant_message import AssistantMessage
from letta_client.types.letta_message_union import LettaMessageUnion
from letta_client.types.user_message import UserMessage
from pydantic import BaseModel
from sqlalchemy import JSON, Column, Text
from sqlmodel import Field, SQLModel
from typing_extensions import Self

ROLE = Literal["user", "yenta"]


# API schemas
class YentaChatInfo(BaseModel):
    conversation_id: str
    name: str


class YentaChatsResponse(BaseModel):
    chats_info: list[YentaChatInfo]


class YentaChatCreationResponse(BaseModel):
    conversation_id: str


class YentaMessageRequest(BaseModel):
    message: str


class YentaMessage(BaseModel):
    content: str
    message_type: str
    role: ROLE

    @classmethod
    def from_message_union(cls, message: LettaMessageUnion) -> Self:
        return cls(
            content=message.content, message_type=message.message_type, role="yenta"
        )


def get_chat_messages(messages: list[LettaMessageUnion]) -> list[YentaMessage]:
    res = []
    for message in messages:
        if isinstance(message, UserMessage):
            res.append(
                YentaMessage(
                    content=message.content,
                    message_type=message.message_type,
                    role="user",
                )
            )
        elif isinstance(message, AssistantMessage):
            res.append(
                YentaMessage(
                    content=message.content,
                    message_type=message.message_type,
                    role="yenta",
                )
            )
    return res


class YentaMessageResponse(BaseModel):
    messages: list[YentaMessage]


class YentaChatHistoryResponse(BaseModel):
    messages: list[YentaMessage]
