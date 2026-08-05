from app.agents.base import BaseAgent
from app.agents.knowledge import KnowledgeAgent
from app.agents.summary import SummaryAgent


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.name] = agent

    def get(self, name: str) -> BaseAgent | None:
        return self._agents.get(name)

    def list(self) -> list[BaseAgent]:
        return list(self._agents.values())


registry = AgentRegistry()
registry.register(KnowledgeAgent())
registry.register(SummaryAgent())
