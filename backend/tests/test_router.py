from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.agents.router import IntentRouter


class FakeAgent(BaseAgent):
    name = "knowledge"
    description = "测试智能体"

    async def invoke(self, context: AgentContext) -> AgentResult:
        return AgentResult(answer="ok", agent_name=self.name)


class FakeSummaryAgent(FakeAgent):
    name = "summary"
    description = "测试总结智能体"


def test_heuristic_routes_summary_keywords():
    router = IntentRouter([FakeAgent(), FakeSummaryAgent()])
    assert router._heuristic("请总结这份文档的核心内容").name == "summary"
    assert router._heuristic("报销流程是什么").name == "knowledge"


def test_heuristic_falls_back_to_first_agent():
    router = IntentRouter([FakeAgent()])
    assert router._heuristic("随便问什么").name == "knowledge"
