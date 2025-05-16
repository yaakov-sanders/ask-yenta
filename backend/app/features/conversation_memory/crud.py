import uuid
from datetime import datetime
from typing import Dict, Optional

from sqlmodel import Session, select

from app.features.conversation_memory.models import ConversationMemory


def get_conversation_memory(db: Session, user_id: str) -> Optional[ConversationMemory]:
    """
    Get a user's conversation memory.
    """
    # Convert string user_id to UUID
    user_uuid = uuid.UUID(user_id)
    statement = select(ConversationMemory).where(ConversationMemory.user_id == user_uuid)
    return db.exec(statement).first()


def update_conversation_memory(
    db: Session, 
    user_id: str, 
    new_message: Dict[str, str], 
    assistant_reply: str, 
    updated_summary: str
) -> ConversationMemory:
    """
    Update a user's conversation memory with a new message, reply, and summary.
    If it doesn't exist, create a new one.
    
    Stores all messages in the conversation history.
    """
    # Convert string user_id to UUID
    user_uuid = uuid.UUID(user_id)
    
    # Get existing memory or create new one
    memory = get_conversation_memory(db, user_id)
    
    if not memory:
        memory = ConversationMemory(
            user_id=user_uuid,
            summary="",
            messages=[],
            updated_at=datetime.utcnow()
        )
    
    # Append new messages
    memory.messages.append(new_message)
    memory.messages.append({"role": "assistant", "content": assistant_reply})
    
    # Update summary and timestamp
    memory.summary = updated_summary
    memory.updated_at = datetime.utcnow()
    
    # Save changes
    db.add(memory)
    db.commit()
    db.refresh(memory)
    
    return memory 