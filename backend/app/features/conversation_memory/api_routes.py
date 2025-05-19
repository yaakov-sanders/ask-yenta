import logging
from http.client import HTTPException

from fastapi import APIRouter, Path, Query
from letta_client.types.agent_state import AgentState

from app.features.conversation_memory.models import (
    ChatConversationCreationResponse,
    ChatConversationInfo,
    ChatConversationsResponse,
    ChatHistoryResponse,
    ChatMessage,
    ChatMessageRequest,
    ChatMessageResponse,
)
from app.features.core.api_deps import CurrentUser
from app.features.llm_logic.llm_logic import (
    create_agent,
    get_agent_by_id,
    get_agents,
    get_messages,
    send_message,
)
from app.features.user_profile.crud import get_or_create_user_profile_block
from app.features.users.models import User

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


async def get_conversation_for_user(current_user: User, chat_conversation_id: str) -> AgentState:
    conversation_agent = await get_agent_by_id(chat_conversation_id)
    if current_user.id not in conversation_agent.identity_ids:
        raise HTTPException(403, "User not part of this conversation")
    return conversation_agent


@router.get("", response_model=ChatConversationsResponse)
async def get_chats(current_user: CurrentUser) -> ChatConversationsResponse:
    conversation_agents = await get_agents(identity_id=current_user.id)
    return ChatConversationsResponse(
        conversations_info=[ChatConversationInfo(conversation_id=a.id, name=a.name) for a in conversation_agents])


@router.post("", response_model=ChatConversationCreationResponse)
async def create_chat(current_user: CurrentUser) -> ChatConversationCreationResponse:
    user_profile_block = await get_or_create_user_profile_block(current_user)
    conversation_agent = await create_agent(identity_ids=[current_user.id], block_ids=[user_profile_block.id])
    return ChatConversationCreationResponse(conversation_id=conversation_agent.id)


@router.post("/{chat_conversation_id}", response_model=ChatMessageResponse)
async def chat_with_memory(
        chat_request: ChatMessageRequest,
        current_user: CurrentUser,
        chat_conversation_id: str = Path(),
) -> ChatMessageResponse:
    conversation_agent = await get_agent_by_id(chat_conversation_id)
    if current_user.id not in conversation_agent.identity_ids:
        raise HTTPException(403, "User not part of this conversation")
    response = await send_message(chat_conversation_id, chat_request.message)
    return ChatMessageResponse(
        messages=[ChatMessage.from_message_union(m) for m in response.messages])


@router.get("/{chat_conversation_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
        current_user: CurrentUser,
        limit: int = Query(10, ge=1, le=50),
        last_message_id: str | None = Query(None),
        chat_conversation_id: str = Path()
) -> ChatHistoryResponse:
    conversation = await get_conversation_for_user(current_user, chat_conversation_id)
    messages = await get_messages(conversation.id, limit, last_message_id)
    return ChatHistoryResponse(
        messages=[ChatMessage.from_message_union(m) for m in messages],
    )
