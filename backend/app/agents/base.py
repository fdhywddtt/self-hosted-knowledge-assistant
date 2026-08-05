from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.chat import Citation


@dataclass
class AgentContext:
    session: AsyncSession
    query: str
    conversation_id: UUID | None = None
    document_id: UUID | None = None
    history: list[dict] = field(default_factory=list)


@dataclass
class AgentResult:
    answer: str
    agent_name: str
    citations: list[Citation] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class BaseAgent(ABC):
    name: str = "base"
    description: str = ""

    @abstractmethod
    async def invoke(self, context: AgentContext) -> AgentResult:
        ...
