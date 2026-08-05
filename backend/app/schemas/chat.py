from uuid import UUID

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: UUID
    document_id: UUID
    filename: str
    page_number: int | None = None
    excerpt: str
    score: float


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=8000)
    conversation_id: UUID | None = None
    document_id: UUID | None = None


class ChatResponse(BaseModel):
    conversation_id: UUID
    answer: str
    agent_name: str
    citations: list[Citation]
