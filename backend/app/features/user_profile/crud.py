import uuid
from datetime import datetime
from typing import Dict, Any

from sqlmodel import Session, select

from app.features.user_profile.models import UserLLMProfile


def upsert_llm_profile(db: Session, user_id: uuid.UUID, new_data: Dict[str, Any]) -> tuple[UserLLMProfile, str]:
    """
    Upsert a user LLM profile. If profile exists and content changed, update profile_data and updated_at.
    If it doesn't exist, insert a new record. If it's unchanged, do nothing.
    
    Returns the profile and status ('created', 'updated', or 'unchanged').
    """
    # Check if profile exists
    statement = select(UserLLMProfile).where(UserLLMProfile.user_id == user_id)
    existing_profile = db.exec(statement).first()
    
    if existing_profile:
        # Check if data has changed
        if existing_profile.profile_data != new_data:
            existing_profile.profile_data = new_data
            existing_profile.updated_at = datetime.utcnow()
            db.add(existing_profile)
            db.commit()
            db.refresh(existing_profile)
            return existing_profile, "updated"
        return existing_profile, "unchanged"
    else:
        # Create new profile
        profile = UserLLMProfile(
            user_id=user_id,
            profile_data=new_data,
            updated_at=datetime.utcnow()
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile, "created"


def get_llm_profile(db: Session, user_id: uuid.UUID) -> UserLLMProfile | None:
    """
    Get a user's LLM profile.
    """
    statement = select(UserLLMProfile).where(UserLLMProfile.user_id == user_id)
    return db.exec(statement).first() 