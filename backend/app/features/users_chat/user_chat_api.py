import logging

from fastapi import APIRouter, Path, Query

from app.features.chat.utils import get_conversation_for_user
from app.features.core.api_deps import CurrentUser
from app.features.letta_logic.letta_logic import (
    create_agent,
    get_agents,
    get_messages,
    send_message,
)
from app.features.users.utils import convert_identity_ids_to_user_ids
from app.features.users_chat.user_chat_models import (
    UsersChatCreationResponse,
    UsersChatHistoryResponse,
    UsersChatInfo,
    UsersChatsResponse,
    UsersMessageRequest,
    UsersMessageResponse,
    get_user_chat_messages,
)

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users-chat", tags=["users-chat"])


@router.get("", response_model=UsersChatsResponse)
async def get_chats(current_user: CurrentUser) -> UsersChatsResponse:
    conversation_agents = await get_agents(
        identity_id=current_user.identity_id, chat_type="users-chat"
    )
    identity_ids = set()
    for agent in conversation_agents:
        identity_ids.update(agent.identity_ids)
    identity_ids_to_user_ids = await convert_identity_ids_to_user_ids(
        list(identity_ids)
    )
    return UsersChatsResponse(
        chats_info=[
            UsersChatInfo(
                conversation_id=a.id,
                name=a.name,
                participant_ids=[
                    identity_ids_to_user_ids.get(
                        ii, "00000000-0000-0000-0000-000000000000"
                    )
                    for ii in a.identity_ids
                ],
            )
            for a in conversation_agents
        ]
    )


@router.post("", response_model=UsersChatCreationResponse)
async def create_chat(current_user: CurrentUser) -> UsersChatCreationResponse:
    conversation_agent = await create_agent(
        identity_ids=[current_user.identity_id],
        block_ids=[current_user.profile_block_id, current_user.yenta_block_id],
        chat_type="users-chat",
    )
    return UsersChatCreationResponse(conversation_id=conversation_agent.id)


@router.post("/{chat_conversation_id}", response_model=UsersMessageResponse)
async def chat_with_memory(
    chat_request: UsersMessageRequest,
    current_user: CurrentUser,
    chat_conversation_id: str = Path(),
) -> UsersMessageResponse:
    await get_conversation_for_user(
        current_user=current_user, chat_conversation_id=chat_conversation_id
    )
    response = await send_message(
        agent_id=chat_conversation_id,
        sender_id=current_user.identity_id,
        message=chat_request.message,
    )
    return UsersMessageResponse(messages=get_user_chat_messages(response.messages))


@router.get("/{chat_conversation_id}", response_model=UsersChatHistoryResponse)
async def get_chat_history(
    current_user: CurrentUser,
    limit: int = Query(10, ge=1, le=50),
    last_message_id: str | None = Query(None),
    chat_conversation_id: str = Path(),
) -> UsersChatHistoryResponse:
    conversation = await get_conversation_for_user(
        current_user=current_user, chat_conversation_id=chat_conversation_id
    )
    messages = await get_messages(
        agent_id=conversation.id, limit=limit, message_id=last_message_id
    )
    return UsersChatHistoryResponse(
        messages=get_user_chat_messages(messages),
    )
