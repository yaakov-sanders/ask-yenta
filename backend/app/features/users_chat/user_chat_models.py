from typing import Literal

from letta_client.types.letta_message_union import LettaMessageUnion
from letta_client.types.user_message import UserMessage
from pydantic import BaseModel

ROLE = Literal["user", "yenta"]


# API schemas
class UsersChatInfo(BaseModel):
    conversation_id: str
    name: str
    participant_ids: list[str]


class UsersChatsResponse(BaseModel):
    chats_info: list[UsersChatInfo]


class UsersChatCreationRequest(BaseModel):
    participant_ids: list[str]


class UsersChatCreationResponse(BaseModel):
    conversation_id: str


class UsersMessageRequest(BaseModel):
    message: str


class UsersChatMessage(BaseModel):
    content: str
    message_type: str
    sender_id: str


def get_user_chat_messages(
    messages: list[LettaMessageUnion],
) -> list[UsersChatMessage]:
    res = []
    for message in messages:
        if isinstance(message, UserMessage):
            res.append(
                UsersChatMessage(
                    content=message.content,
                    message_type=message.message_type,
                    sender_id=message.sender_id,
                )
            )
    return res


class UsersMessageResponse(BaseModel):
    messages: list[UsersChatMessage]


class UsersChatHistoryResponse(BaseModel):
    messages: list[UsersChatMessage]
