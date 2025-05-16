import uuid
from datetime import datetime
from typing import Dict, Any, TYPE_CHECKING

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, JSON

# Use TYPE_CHECKING for circular imports
if TYPE_CHECKING:
    from app.features.users.models import User


class UserLLMProfileBase(SQLModel):
    profile_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserLLMProfile(UserLLMProfileBase, table=True):
    __tablename__ = "user_llm_profile"
    
    user_id: uuid.UUID = Field(primary_key=True, foreign_key="user.id")
    # Removing relationship to User


# API schemas
class UserProfileText(BaseModel):
    text: str


class UserProfileResponse(BaseModel):
    status: str
    profile: Dict[str, Any]


class DirectLLMPrompt(BaseModel):
    prompt: str


class LLMResponse(BaseModel):
    response: str


class UserLLMProfileRead(UserLLMProfileBase):
    user_id: uuid.UUID 