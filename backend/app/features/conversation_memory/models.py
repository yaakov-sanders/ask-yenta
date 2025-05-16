import uuid
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON, Text


class ConversationMemory(SQLModel, table=True):
    __tablename__ = "conversation_memory"
    
    user_id: uuid.UUID = Field(primary_key=True)
    summary: str = Field(default="", sa_column=Column(Text))
    messages: List[Dict[str, str]] = Field(default=[], sa_column=Column(JSON))
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# API schemas
class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    updated_summary: str 