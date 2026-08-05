from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentContext
from app.agents.registry import registry
from app.agents.router import IntentRouter
from app.api.deps import get_db, verify_api_key
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.memory import append_message, get_or_create_conversation, list_messages

router = APIRouter(prefix="/chat", tags=["chat"], dependencies=[Depends(verify_api_key)])


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: AsyncSession = Depends(get_db)):
    conversation = await get_or_create_conversation(db, payload.conversation_id)
    history = await list_messages(db, conversation.id, limit=20)
    await append_message(db, conversation.id, "user", payload.question)

    intent_router = IntentRouter(registry.list())
    agent = await intent_router.route(payload.question)
    context = AgentContext(
        session=db,
        query=payload.question,
        conversation_id=conversation.id,
        document_id=payload.document_id,
        history=[{"role": message.role, "content": message.content} for message in history],
    )
    result = await agent.invoke(context)

    await append_message(
        db,
        conversation.id,
        "assistant",
        result.answer,
        agent_name=result.agent_name,
        citations=[citation.model_dump(mode="json") for citation in result.citations],
    )
    return ChatResponse(
        conversation_id=conversation.id,
        answer=result.answer,
        agent_name=result.agent_name,
        citations=result.citations,
    )
