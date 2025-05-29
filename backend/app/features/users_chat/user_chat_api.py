import logging

from fastapi import APIRouter, Path, Query
from letta_client import CreateBlock

from app.features.chat.chat_utils import get_conversation_for_user
from app.features.connections.connections_utils import validate_connections
from app.features.core.api_deps import CurrentUser
from app.features.letta_logic.letta_logic import (
    create_agent,
    get_agents,
    get_messages,
    send_message_to_users_chat,
    create_block,
)
from app.features.users_chat.user_chat_models import (
    UsersChatCreationResponse,
    UsersChatHistoryResponse,
    UsersChatInfo,
    UsersChatsResponse,
    UsersMessageRequest,
    UsersMessageResponse,
    get_user_chat_messages,
    UsersChatCreationRequest,
)

# Set up logger
logger = logging.getLogger(__name__)

users_chat_router = APIRouter(prefix="/users-chat", tags=["users-chat"])


@users_chat_router.get("", response_model=UsersChatsResponse)
async def get_chats(current_user: CurrentUser) -> UsersChatsResponse:
    conversation_agents = await get_agents(
        user_id=current_user.id, chat_type="users-chat"
    )
    user_ids = set()
    for agent in conversation_agents:
        user_ids.update(agent.tags)
    return UsersChatsResponse(
        chats_info=[
            UsersChatInfo(
                conversation_id=a.id,
                name=a.name,
                participant_ids=[ui for ui in user_ids if len(ui) == 36],
            )
            for a in conversation_agents
        ]
    )


@users_chat_router.post("", response_model=UsersChatCreationResponse)
async def create_chat(
    chat_request: UsersChatCreationRequest, current_user: CurrentUser
) -> UsersChatCreationResponse:
    await validate_connections(current_user.id, chat_request.participant_ids)
    interactions_block = await create_block("interactions", "")
    conversation_agent = await create_agent(
        user_ids=chat_request.participant_ids + [current_user.id],
        chat_type="users-chat",
        tools=["summarize_interaction"],
        block_ids=[interactions_block.id],
        memory_blocks=[
            CreateBlock(
                label="persona",
                value="""You are Yenta. You silently observe this group chat. Your job is to track what each participant shares, learns, or reveals throughout the conversation.
For each message, determine if it expresses something meaningful — such as plans, preferences, opinions, or relationship dynamics.
You will receive messages in the following format: {user_id}:{message_content}
When it does, use the `summarize_interaction` tool to capture:
- who said it,
- the original message,
- and a clear, concise insight about what was revealed.
Only store meaningful takeaways, not every message. Do not reply to users.
""",
            ),
        ],
    )
    return UsersChatCreationResponse(conversation_id=conversation_agent.id)


@users_chat_router.post("/{chat_conversation_id}", response_model=UsersMessageResponse)
async def chat_with_memory(
    chat_request: UsersMessageRequest,
    current_user: CurrentUser,
    chat_conversation_id: str = Path(),
) -> UsersMessageResponse:
    await get_conversation_for_user(
        current_user=current_user, chat_conversation_id=chat_conversation_id
    )
    response = await send_message_to_users_chat(
        agent_id=chat_conversation_id,
        sender_id=current_user.id,
        message=chat_request.message,
    )
    messages = await get_user_chat_messages(response.messages)
    return UsersMessageResponse(messages=messages)


@users_chat_router.get(
    "/{chat_conversation_id}", response_model=UsersChatHistoryResponse
)
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
    messages = await get_user_chat_messages(messages)

    return UsersChatHistoryResponse(messages=messages)
