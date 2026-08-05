from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ConversationRead(ORMModel):
    id: UUID
    title: str | None = None
    created_at: datetime
    updated_at: datetime


class MessageRead(ORMModel):
    id: UUID
    role: str
    content: str
    agent_name: str | None = None
    citations: list[dict]
    created_at: datetime
