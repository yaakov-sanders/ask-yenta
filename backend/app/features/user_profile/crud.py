import uuid
from datetime import datetime
from typing import Any, Tuple

from letta_client.types.block import Block
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import save_to_db
from app.features.llm_logic.llm_logic import create_block, get_block_by_id
from app.features.user_profile.models import UserLLMProfile
from app.features.users.models import User


async def upsert_llm_profile(db: AsyncSession, user_id: uuid.UUID, new_data: dict[str, Any]) -> tuple[
    UserLLMProfile, str]:
    """
    Upsert a user LLM profile. If profile exists and content changed, update profile_data and updated_at.
    If it doesn't exist, insert a new record. If it's unchanged, do nothing.

    Returns the profile and status ('created', 'updated', or 'unchanged').
    """
    # Check if profile exists
    statement = select(UserLLMProfile).where(UserLLMProfile.user_id == user_id)
    result = await db.exec(statement)
    existing_profile = result.first()

    if existing_profile:
        # Check if data has changed
        if existing_profile.profile_data != new_data:
            existing_profile.profile_data = new_data
            existing_profile.updated_at = datetime.utcnow()
            db.add(existing_profile)
            await db.commit()
            await db.refresh(existing_profile)
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
        await db.commit()
        await db.refresh(profile)
        return profile, "created"


async def get_llm_profile(db: AsyncSession, user_id: uuid.UUID) -> UserLLMProfile | None:
    """
    Get a user's LLM profile.
    """
    statement = select(UserLLMProfile).where(UserLLMProfile.user_id == user_id)
    result = await db.exec(statement)
    return result.first()


async def get_or_create_user_block_ids(user: User) -> Tuple[str, str]:
    if user.profile_block_id:
        profile_block_id = user.profile_block_id
    else:
        profile_block = await create_block('human', f"Profile: {user.full_name}")
        profile_block_id = profile_block.id
        user.profile_block_id = profile_block_id

        await save_to_db(user)
    if user.yenta_block_id:
        yenta_block_id = user.yenta_block_id
    else:
        yenta_block = await create_block('persona', f"You are Yenta — a warm, witty, and perceptive AI who remembers everything about the user and helps them understand themselves and others better. You speak like a nosy best friend with good intentions and great instincts. Be smart, honest, and a little cheeky.")
        yenta_block_id = yenta_block.id
        user.yenta_block_id = yenta_block_id
        await save_to_db(user)

    return profile_block_id, yenta_block_id
