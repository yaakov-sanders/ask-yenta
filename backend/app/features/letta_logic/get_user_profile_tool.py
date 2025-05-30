import httpx
import os
from pydantic import BaseModel, Field


class UserProfileResponse(BaseModel):
    """Response model for user profile data"""

    value: str = Field(..., description="The user's profile block value")


def get_user_profile(user_id: str) -> str:
    """Get the user's profile information from the backend.

    Args:
        user_id (str): The user id of the user we want to get the profile for

    Returns:
        str: The user's profile block value
    """
    try:
        backend_url = os.getenv("BACKEND_URL", "http://backend:8000")
        response = httpx.get(f"{backend_url}/api/v1/yenta-chat/profile-block/{user_id}")
        response.raise_for_status()

        # Parse and return the profile value
        profile_data = response.json()
        return profile_data["value"]
    except Exception:
        return f"Couldn't access users profile"
