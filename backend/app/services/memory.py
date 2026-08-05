from uuid import UUID

from sqlalchemy import select

from app.db.models import Conversation, Message


async def get_or_create_conversation(session, conversation_id: UUID | None) -> Conversation:
    if conversation_id:
        conversation = await session.get(Conversation, conversation_id)
        if conversation:
            return conversation
    conversation = Conversation()
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation


async def append_message(
    session,
    conversation_id: UUID,
    role: str,
    content: str,
    agent_name: str | None = None,
    citations: list | None = None,
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        agent_name=agent_name,
        citations=citations or [],
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


async def list_conversations(session, limit: int = 50) -> list[Conversation]:
    result = await session.execute(
        select(Conversation).order_by(Conversation.updated_at.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def list_messages(session, conversation_id: UUID, limit: int = 50) -> list[Message]:
    result = await session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
    )
    return list(result.scalars().all())
