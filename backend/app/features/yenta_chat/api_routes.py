import logging
from http.client import HTTPException

from fastapi import APIRouter, Path, Query
from letta_client.types.agent_state import AgentState

from app.features.core.api_deps import CurrentUser
from app.features.letta_logic.letta_logic import (
    create_agent,
    get_agent_by_id,
    get_agents,
    get_messages,
    send_message,
)
from app.features.user_profile.crud import get_or_create_user_block_ids
from app.features.users.models import User
from app.features.yenta_chat.models import (
    YentaChatCreationResponse,
    YentaChatHistoryResponse,
    YentaChatInfo,
    YentaChatsResponse,
    YentaMessageRequest,
    YentaMessageResponse,
    get_chat_messages,
)

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/yenta-chat", tags=["yenta-chat"])


async def get_conversation_for_user(
    current_user: User, chat_conversation_id: str
) -> AgentState:
    conversation_agent = await get_agent_by_id(chat_conversation_id)
    if str(current_user.id) not in conversation_agent.tags:
        raise HTTPException(403, "User not part of this conversation")
    return conversation_agent


@router.get("", response_model=YentaChatsResponse)
async def get_chats(current_user: CurrentUser) -> YentaChatsResponse:
    conversation_agents = await get_agents(identity_id=current_user.id)
    return YentaChatsResponse(
        chats_info=[
            YentaChatInfo(conversation_id=a.id, name=a.name)
            for a in conversation_agents
        ]
    )


@router.post("", response_model=YentaChatCreationResponse)
async def create_chat(current_user: CurrentUser) -> YentaChatCreationResponse:
    conversation_agent = await create_agent(
        identity_ids=[current_user.identity_id],
        block_ids=[current_user.profile_block_id, current_user.yenta_block_id],
    )
    return YentaChatCreationResponse(conversation_id=conversation_agent.id)


@router.post("/{chat_conversation_id}", response_model=YentaMessageResponse)
async def chat_with_memory(
    chat_request: YentaMessageRequest,
    current_user: CurrentUser,
    chat_conversation_id: str = Path(),
) -> YentaMessageResponse:
    await get_conversation_for_user(current_user, chat_conversation_id)
    response = await send_message(chat_conversation_id, chat_request.message)
    return YentaMessageResponse(messages=get_chat_messages(response.messages))


@router.get("/{chat_conversation_id}", response_model=YentaChatHistoryResponse)
async def get_chat_history(
    current_user: CurrentUser,
    limit: int = Query(10, ge=1, le=50),
    last_message_id: str | None = Query(None),
    chat_conversation_id: str = Path(),
) -> YentaChatHistoryResponse:
    conversation = await get_conversation_for_user(current_user, chat_conversation_id)
    messages = await get_messages(conversation.id, limit, last_message_id)
    return YentaChatHistoryResponse(
        messages=get_chat_messages(messages),
    )
