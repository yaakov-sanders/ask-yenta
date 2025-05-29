from fastapi import HTTPException
from letta_client import AgentState

from app.features.users.users_models import User
from app.features.letta_logic.letta_logic import get_agent_by_id


async def get_conversation_for_user(
    current_user: User, chat_conversation_id: str
) -> AgentState:
    conversation_agent = await get_agent_by_id(chat_conversation_id)
    if str(current_user.id) not in conversation_agent.tags:
        raise HTTPException(403, "User not part of this conversation")
    return conversation_agent
