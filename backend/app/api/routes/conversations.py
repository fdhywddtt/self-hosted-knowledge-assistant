from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, verify_api_key
from app.db.models import Conversation
from app.schemas.common import ConversationRead, MessageRead
from app.services.memory import list_conversations, list_messages

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("", response_model=list[ConversationRead])
async def conversations(db: AsyncSession = Depends(get_db)):
    return await list_conversations(db)


@router.get("/{conversation_id}/messages", response_model=list[MessageRead])
async def conversation_messages(conversation_id: UUID, db: AsyncSession = Depends(get_db)):
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="会话不存在")
    return await list_messages(db, conversation_id)
