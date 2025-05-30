import logging
import re
from typing import Annotated

from fastapi import APIRouter, Path, Query, Depends, HTTPException

from app.features.chat.chat_utils import get_conversation_for_user
from app.features.core.api_deps import CurrentUser, LettaAgentKey
from app.features.letta_logic.letta_logic import (
    create_agent,
    get_agents,
    get_messages,
    send_message_to_yenta,
    get_block_by_id,
)
from app.features.users.users_crud import get_users_by_ids
from app.features.yenta_chat.yenta_chat_models import (
    YentaChatCreationResponse,
    YentaChatHistoryResponse,
    YentaChatInfo,
    YentaChatsResponse,
    YentaMessageRequest,
    YentaMessageResponse,
    get_yenta_chat_messages,
)

# Set up logger
logger = logging.getLogger(__name__)

yenta_chat_router = APIRouter(prefix="/yenta-chat", tags=["yenta-chat"])


@yenta_chat_router.get("", response_model=YentaChatsResponse)
async def get_chats(current_user: CurrentUser) -> YentaChatsResponse:
    conversation_agents = await get_agents(
        user_id=current_user.id, chat_type="yenta-chat"
    )
    return YentaChatsResponse(
        chats_info=[
            YentaChatInfo(conversation_id=a.id, name=a.name)
            for a in conversation_agents
        ]
    )


@yenta_chat_router.post("", response_model=YentaChatCreationResponse)
async def create_chat(current_user: CurrentUser) -> YentaChatCreationResponse:
    conversation_agent = await create_agent(
        user_ids=[current_user.id],
        chat_type="yenta-chat",
        block_ids=[current_user.profile_block_id, current_user.yenta_block_id],
    )
    return YentaChatCreationResponse(conversation_id=conversation_agent.id)


@yenta_chat_router.post("/{chat_conversation_id}", response_model=YentaMessageResponse)
async def chat_with_memory(
    chat_request: YentaMessageRequest,
    current_user: CurrentUser,
    chat_conversation_id: str = Path(),
) -> YentaMessageResponse:
    await get_conversation_for_user(
        current_user=current_user, chat_conversation_id=chat_conversation_id
    )

    # Extract mentioned user IDs from the message text
    mention_pattern = r"@\[.*?\]\((.*?)\)"
    mentioned_ids = re.findall(mention_pattern, chat_request.message)

    response = await send_message_to_yenta(
        current_user_id=current_user.id,
        agent_id=chat_conversation_id,
        message=chat_request.message,
        mentioned_ids=mentioned_ids,
    )
    return YentaMessageResponse(messages=get_yenta_chat_messages(response.messages))


@yenta_chat_router.get(
    "/{chat_conversation_id}", response_model=YentaChatHistoryResponse
)
async def get_chat_history(
    current_user: CurrentUser,
    limit: int = Query(10, ge=1, le=50),
    last_message_id: str | None = Query(None),
    chat_conversation_id: str = Path(),
) -> YentaChatHistoryResponse:
    conversation = await get_conversation_for_user(
        current_user=current_user, chat_conversation_id=chat_conversation_id
    )
    messages = await get_messages(
        agent_id=conversation.id, limit=limit, message_id=last_message_id
    )
    return YentaChatHistoryResponse(
        messages=get_yenta_chat_messages(messages),
    )


@yenta_chat_router.get("/profile-block/{user_id}")
async def get_user_profile_block(user_id: str = Path()) -> dict:
    """
    Get a user's profile block value
    """
    users = await get_users_by_ids([user_id])

    if not users:
        raise HTTPException(404, "User not found")
    block = await get_block_by_id(users[0].profile_block_id)
    return {"value": block.value}
