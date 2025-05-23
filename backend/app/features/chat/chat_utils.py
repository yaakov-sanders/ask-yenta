from fastapi import HTTPException
from letta_client import AgentState

from app.features.letta_logic.letta_logic import get_agent_by_id
from app.features.users.users_models import User


async def get_conversation_for_user(
    current_user: User, chat_conversation_id: str
) -> AgentState:
    conversation_agent = await get_agent_by_id(chat_conversation_id)
    if current_user.identity_id not in conversation_agent.identity_ids:
        raise HTTPException(403, "User not part of this conversation")
    return conversation_agent
