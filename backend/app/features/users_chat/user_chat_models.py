from typing import Literal

from letta_client.types.letta_message_union import LettaMessageUnion
from letta_client.types.user_message import UserMessage
from pydantic import BaseModel

from app.features.users.users_utils import convert_identity_ids_to_user_ids

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


async def get_user_chat_messages(
    messages: list[LettaMessageUnion],
) -> list[UsersChatMessage]:
    res = []
    identity_ids = {
        m.sender_id for m in messages if hasattr(m, "sender_id") and m.sender_id
    }
    identity_ids_to_user_ids = await convert_identity_ids_to_user_ids(
        list(identity_ids)
    )
    for message in messages:
        if (
            isinstance(message, UserMessage)
            and message.sender_id in identity_ids_to_user_ids
        ):
            res.append(
                UsersChatMessage(
                    content=message.content,
                    message_type=message.message_type,
                    sender_id=identity_ids_to_user_ids[message.sender_id],
                )
            )
    return res


class UsersMessageResponse(BaseModel):
    messages: list[UsersChatMessage]


class UsersChatHistoryResponse(BaseModel):
    messages: list[UsersChatMessage]
