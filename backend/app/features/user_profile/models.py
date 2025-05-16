import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

# Use TYPE_CHECKING for circular imports
if TYPE_CHECKING:
    pass


class UserLLMProfileBase(SQLModel):
    profile_data: dict[str, Any] = Field(default={}, sa_column=Column(JSON))
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
    profile: dict[str, Any]


class DirectLLMPrompt(BaseModel):
    prompt: str


class LLMResponse(BaseModel):
    response: str


class UserLLMProfileRead(UserLLMProfileBase):
    user_id: uuid.UUID
