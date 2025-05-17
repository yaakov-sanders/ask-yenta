import logging
import uuid
from datetime import datetime

from sqlalchemy.orm import attributes
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.features.conversation_memory.models import ConversationMemory

# Setup logging
logger = logging.getLogger(__name__)

async def get_conversation_memory(db: AsyncSession, user_id: str) -> ConversationMemory | None:
    """
    Get a user's conversation memory.
    """
    # Convert string user_id to UUID
    user_uuid = uuid.UUID(user_id)
    statement = select(ConversationMemory).where(ConversationMemory.user_id == user_uuid)
    result = await db.exec(statement)
    return result.first()


async def get_conversation_history(
    db: AsyncSession,
    user_id: str,
    limit: int = 10,
    offset: int = 0
) -> tuple[list[dict[str, str]], int]:
    """
    Get a paginated view of conversation history.

    Args:
        db: Database session
        user_id: User ID
        limit: Maximum number of messages to retrieve
        offset: Number of messages to skip

    Returns:
        A tuple containing (messages, total_count)
    """
    memory = await get_conversation_memory(db, user_id)

    if not memory or not memory.messages:
        return [], 0

    total_count = len(memory.messages)

    # Get messages in reverse order (newest first) with pagination
    start_idx = max(0, total_count - offset - limit)
    end_idx = max(0, total_count - offset)

    # Return messages in chronological order (oldest first)
    messages = memory.messages[start_idx:end_idx]

    return messages, total_count


async def update_conversation_memory(
    db: AsyncSession,
    user_id: str,
    new_message: dict[str, str],
    assistant_reply: str,
    updated_summary: str
) -> ConversationMemory:
    """
    Update a user's conversation memory with a new message, reply, and summary.
    If it doesn't exist, create a new one.

    Stores all messages in the conversation history.
    """
    try:
        # Convert string user_id to UUID
        user_uuid = uuid.UUID(user_id)

        # Get existing memory or create new one
        memory = await get_conversation_memory(db, user_id)

        if not memory:
            memory = ConversationMemory(
                user_id=user_uuid,
                summary="",
                messages=[],
                updated_at=datetime.utcnow()
            )

        # Append new messages
        if memory.messages is None:
            memory.messages = []

        # Create a completely new list with the existing messages plus new ones
        # This ensures SQLAlchemy detects the change
        new_messages = memory.messages.copy() if memory.messages else []
        new_messages.append(new_message)
        new_messages.append({"role": "assistant", "content": assistant_reply})
        memory.messages = new_messages  # Replace the entire list

        # Update summary and timestamp
        memory.summary = updated_summary
        memory.updated_at = datetime.utcnow()

        # Force-mark the messages column as modified
        # This is necessary for SQLAlchemy to detect changes to JSON fields
        attributes.flag_modified(memory, "messages")

        # Save changes
        db.add(memory)
        await db.commit()
        await db.refresh(memory)

        return memory

    except Exception as e:
        logger.error(f"Error in update_conversation_memory: {str(e)}", exc_info=True)
        # Re-raise the exception to be handled by the caller
        raise
