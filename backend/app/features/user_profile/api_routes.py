import uuid
import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from app.features.core.api_deps import CurrentUser, SessionDep
from app.features.user_profile.crud import get_llm_profile, upsert_llm_profile
from app.features.user_profile.llm import parse_profile_from_text, summarize_profile_data, update_profile_from_text as update_profile_data_from_text
from app.features.user_profile.models import (
    UserLLMProfileRead,
    UserLLMProfileSummary,
    UserProfileResponse,
    UserProfileText,
    UserProfileUpdate,
)
from app.features.users.models import User

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["user-profile"])


@router.post("/{user_id}/profile-text", response_model=UserProfileResponse)
async def create_profile_from_text(
    user_id: uuid.UUID,
    profile_text: UserProfileText,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Create a new user profile from free-form text, which will be parsed by an LLM
    into structured JSON and stored in the database.
    
    Returns 409 Conflict if a profile already exists for this user.
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
        # Check if the user already has a profile
        existing_profile = get_llm_profile(session, user_id)
        
        if existing_profile:
            # Return conflict if profile already exists
            raise HTTPException(
                status_code=409, 
                detail="Profile already exists. Use PUT to update an existing profile."
            )
        
        # Parse the free-form text using LLM for new profile
        parsed_profile = parse_profile_from_text(profile_text.text)
        
        # Create a new profile
        profile, status = upsert_llm_profile(session, user_id, parsed_profile)

        return UserProfileResponse(status=status, profile=profile.profile_data)
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log and wrap other exceptions
        logger.error(f"Error creating profile: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}/profile-text", response_model=UserProfileResponse)
async def update_profile_from_text(
    user_id: uuid.UUID,
    profile_text: UserProfileText,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Update an existing user profile with free-form text.
    
    The LLM will analyze the existing profile and the new text,
    then intelligently merge them to create an updated profile.
    
    Returns 404 Not Found if no profile exists for this user.
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
        # Get the existing profile
        existing_profile = get_llm_profile(session, user_id)
        
        if not existing_profile:
            # Return not found if profile doesn't exist
            raise HTTPException(
                status_code=404, 
                detail="Profile not found. Use POST to create a new profile."
            )
        
        # Update existing profile with the new text
        updated_profile = update_profile_data_from_text(
            existing_profile.profile_data, 
            profile_text.text
        )
        
        # Save the updated profile
        profile, status = upsert_llm_profile(session, user_id, updated_profile)

        return UserProfileResponse(status=status, profile=profile.profile_data)
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log and wrap other exceptions
        logger.error(f"Error updating profile: {str(e)}", exc_info=True)
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


@router.get("/{user_id}/profile", response_model=UserLLMProfileSummary)
async def get_user_profile(
    user_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get the user profile summary generated by the LLM.
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
    db_profile = get_llm_profile(session, user_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Generate profile summary
    try:
        summary = summarize_profile_data(db_profile.profile_data)
        
        # Create a UserLLMProfileSummary instance for the response
        profile_summary = UserLLMProfileSummary(
            user_id=db_profile.user_id,
            profile_summary=summary,
            updated_at=db_profile.updated_at
        )
        
        return profile_summary
    except Exception as e:
        # If summarization fails, log the error and fail the request
        logger.error(f"Failed to summarize profile: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Unable to generate profile summary. Please try again later."
        )
