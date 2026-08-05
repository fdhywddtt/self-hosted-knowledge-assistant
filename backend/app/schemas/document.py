from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    content_type: str
    status: str
    error: str | None = None
    created_at: datetime


class DocumentListResponse(BaseModel):
    items: list[DocumentRead]


class UploadResponse(BaseModel):
    id: UUID
    filename: str
    status: str
