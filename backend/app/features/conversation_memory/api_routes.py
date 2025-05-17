from typing import Any
import asyncio
import logging

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
from app.features.user_profile.llm import analyze_message_for_profile_updates
from app.features.user_profile.llm import analyze_message_for_initial_profile
from app.features.user_profile.crud import get_llm_profile, upsert_llm_profile

# Set up logger
logger = logging.getLogger(__name__)

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
    Includes user's LLM profile if available.
    Simultaneously checks if the user's profile needs to be updated based on the message.
    If no profile exists, creates one if the message contains relevant profile information.
    """
    user_id = chat_request.user_id
    user_message = chat_request.message

    # Get existing conversation memory or initialize empty
    memory = get_conversation_memory(session, user_id)

    # Get current summary and messages
    summary = memory.summary if memory and memory.summary else "No previous context available."
    messages = memory.messages if memory and memory.messages else []

    # Get user's LLM profile if available
    user_profile = get_llm_profile(session, user_id)
    profile_data = user_profile.profile_data if user_profile else {}

    try:
        # Process chat response
        chat_task = llm_chat_with_memory(
            user_message=user_message,
            summary=summary,
            conversation_history=messages,
            user_profile=profile_data
        )
        
        if user_profile:
            # If profile exists, check for updates
            profile_task = analyze_message_for_profile_updates(profile_data, user_message)
            reply_results, profile_results = await asyncio.gather(chat_task, profile_task)
            
            reply, updated_summary = reply_results
            updated_profile_data, was_profile_updated = profile_results
            
            # Update profile if changes were detected
            if was_profile_updated:
                profile, status = upsert_llm_profile(session, user_id, updated_profile_data)
                logger.info(f"User profile updated for user {user_id} with status: {status}")
        else:
            # If no profile exists, check if we should create one
            profile_task = analyze_message_for_initial_profile(user_message)
            reply_results, profile_results = await asyncio.gather(chat_task, profile_task)
            
            reply, updated_summary = reply_results
            initial_profile_data, should_create_profile = profile_results
            
            # Create a new profile if the message contains relevant information
            if should_create_profile and initial_profile_data:
                profile, status = upsert_llm_profile(session, user_id, initial_profile_data)
                logger.info(f"New user profile created for user {user_id} with status: {status}")
            else:
                # No profile exists and message doesn't warrant creating one
                logger.debug(f"No profile exists for user {user_id} and message doesn't warrant creating one")

        # Create new message object
        new_message = {"role": "user", "content": user_message}

        # Update conversation memory
        update_conversation_memory(session, user_id, new_message, reply, updated_summary)

        return ChatResponse(reply=reply, updated_summary=updated_summary)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
