from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.features.conversation_memory.crud import (
    get_conversation_history,
    get_conversation_memory,
    update_conversation_memory,
)
from app.features.conversation_memory.models import (
    ChatHistoryResponse,
    ChatRequest,
    ChatResponse,
)
from app.features.core.api_deps import CurrentUser, SessionDep
from app.features.user_profile.llm import chat_with_memory as llm_chat_with_memory

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    user_id: str,
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    session: SessionDep = None,
    current_user: CurrentUser = None,
) -> ChatHistoryResponse:
    """
    Get chat history for a user with pagination.
    Returns the most recent messages first.

    - **user_id**: ID of the user to get chat history for
    - **limit**: Maximum number of messages to retrieve (default: 10, max: 50)
    - **offset**: Number of messages to skip for pagination (default: 0)
    """
    try:
        messages, total_count = get_conversation_history(
            db=session,
            user_id=user_id,
            limit=limit,
            offset=offset
        )

        has_more = total_count > (offset + len(messages))

        return ChatHistoryResponse(
            messages=messages,
            has_more=has_more,
            total_count=total_count
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")


@router.post("", response_model=ChatResponse)
async def chat_with_memory(
    chat_request: ChatRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Chat with the LLM using hybrid memory (summary + recent messages).
    Updates the conversation memory and returns the assistant's reply with the updated summary.
    """
    user_id = chat_request.user_id
    user_message = chat_request.message

    # Get existing conversation memory or initialize empty
    memory = get_conversation_memory(session, user_id)

    # Get current summary and messages
    summary = memory.summary if memory and memory.summary else "No previous context available."
    messages = memory.messages if memory and memory.messages else []

    try:
        # Call the centralized LLM function
        reply, updated_summary = llm_chat_with_memory(
            user_message=user_message,
            summary=summary,
            conversation_history=messages
        )

        # Create new message object
        new_message = {"role": "user", "content": user_message}

        # Update conversation memory
        update_conversation_memory(session, user_id, new_message, reply, updated_summary)

        return ChatResponse(reply=reply, updated_summary=updated_summary)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
