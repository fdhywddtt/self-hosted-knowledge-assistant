import json

from app.agents.base import BaseAgent
from app.agents.knowledge import KnowledgeAgent
from app.agents.summary import SummaryAgent
from app.core.config import get_settings
from app.services.llm import get_llm_provider

SUMMARY_KEYWORDS = ("总结", "摘要", "归纳", "概述", "概览", "要点", "summarize", "summary")


class IntentRouter:
    """先尝试 LLM 结构化路由，失败或无真实模型时回退到关键词规则。"""

    def __init__(self, agents: list[BaseAgent] | None = None):
        self.agents = agents or [KnowledgeAgent(), SummaryAgent()]

    async def route(self, query: str) -> BaseAgent:
        settings = get_settings()
        if settings.llm_provider != "dummy":
            try:
                llm = get_llm_provider()
                prompt = (
                    "从以下智能体中选择最适合回答用户问题的智能体，只返回 JSON："
                    '{"agent": "名称"}\n'
                    "智能体：\n"
                    + "\n".join(f"- {agent.name}: {agent.description}" for agent in self.agents)
                )
                raw = await llm.complete(
                    [{"role": "user", "content": f"{prompt}\n\n用户问题：{query}"}],
                    response_format={"type": "json_object"},
                )
                data = json.loads(raw)
                agent = self._by_name(str(data.get("agent", "")))
                if agent:
                    return agent
            except Exception:
                pass
        return self._heuristic(query)

    def _heuristic(self, query: str) -> BaseAgent:
        lowered = query.lower()
        if any(keyword in lowered for keyword in SUMMARY_KEYWORDS):
            return self._by_name("summary") or self.agents[0]
        return self._by_name("knowledge") or self.agents[0]

    def _by_name(self, name: str) -> BaseAgent | None:
        return next((agent for agent in self.agents if agent.name == name), None)
