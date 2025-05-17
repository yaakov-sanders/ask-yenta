import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.features.core.api_deps import CurrentUser, SessionDep
from app.features.user_profile.crud import get_llm_profile, upsert_llm_profile
from app.features.user_profile.llm import parse_profile_from_text
from app.features.user_profile.models import (
    UserLLMProfileRead,
    UserProfileResponse,
    UserProfileText,
    UserProfileUpdate,
)
from app.features.users.models import User

router = APIRouter(prefix="/users", tags=["user-profile"])


@router.post("/{user_id}/profile-text", response_model=UserProfileResponse)
async def submit_profile_text(
    user_id: uuid.UUID,
    profile_text: UserProfileText,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Submit free-form text about a user, which will be parsed by an LLM
    into structured JSON and stored in the database.
    """
    # Check if user exists
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check permissions (only superusers can update other user profiles)
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to update other user's profile"
        )

    try:
        # Parse the free-form text using LLM
        parsed_profile = parse_profile_from_text(profile_text.text)

        # Upsert the profile in the database
        profile, status = upsert_llm_profile(session, user_id, parsed_profile)

        return UserProfileResponse(status=status, profile=profile.profile_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{user_id}/profile", response_model=UserProfileResponse)
async def update_user_profile(
    user_id: uuid.UUID,
    profile_update: UserProfileUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Update an existing user profile directly with provided data.
    """
    # Check if user exists
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check permissions (only superusers can update other user profiles)
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to update other user's profile"
        )

    # Get existing profile
    existing_profile = get_llm_profile(session, user_id)
    if not existing_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Merge the existing profile with the updates
    updated_data = existing_profile.profile_data.copy()

    # Add or update fields
    for key, value in profile_update.data.items():
        if value is not None:
            updated_data[key] = value
        elif key in updated_data:
            # Remove keys with None values
            del updated_data[key]

    # Upsert the updated profile
    profile, status = upsert_llm_profile(session, user_id, updated_data)

    return UserProfileResponse(status=status, profile=profile.profile_data)


@router.get("/{user_id}/profile", response_model=UserLLMProfileRead)
async def get_user_profile(
    user_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get the structured user profile.
    """
    # Check if user exists
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check permissions (only superusers can view other user profiles)
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to view other user's profile"
        )

    # Get the profile
    profile = get_llm_profile(session, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile
