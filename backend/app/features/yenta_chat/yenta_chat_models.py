from typing import Literal

from letta_client.types.assistant_message import AssistantMessage
from letta_client.types.letta_message_union import LettaMessageUnion
from letta_client.types.user_message import UserMessage
from pydantic import BaseModel

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
    mentioned_user_ids: list[str] = []


class YentaChatMessage(BaseModel):
    content: str
    message_type: str
    role: ROLE


def get_yenta_chat_messages(
    messages: list[LettaMessageUnion],
) -> list[YentaChatMessage]:
    res = []
    for message in messages:
        if isinstance(message, UserMessage):
            res.append(
                YentaChatMessage(
                    content=message.content,
                    message_type=message.message_type,
                    role="user",
                )
            )
        elif isinstance(message, AssistantMessage):
            res.append(
                YentaChatMessage(
                    content=message.content,
                    message_type=message.message_type,
                    role="yenta",
                )
            )
    return res


class YentaMessageResponse(BaseModel):
    messages: list[YentaChatMessage]


class YentaChatHistoryResponse(BaseModel):
    messages: list[YentaChatMessage]
