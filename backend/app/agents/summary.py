from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.core.config import get_settings
from app.services.citations import build_citations
from app.services.llm import get_llm_provider
from app.services.reranking import get_reranker
from app.services.retrieval import hybrid_search


class SummaryAgent(BaseAgent):
    name = "summary"
    description = "总结知识库中文档的核心内容，适合总结、摘要、归纳"

    async def invoke(self, context: AgentContext) -> AgentResult:
        settings = get_settings()
        rows = await hybrid_search(
            context.session,
            context.query,
            top_k=settings.top_k * 2,
            document_id=context.document_id,
        )
        reranker = get_reranker()
        rows = await reranker.rerank(context.query, rows, settings.rerank_top_k * 2)

        if not rows:
            return AgentResult(
                answer="知识库中暂时没有找到可总结的内容。",
                agent_name=self.name,
            )

        context_text = "\n\n".join(f"[材料 {index + 1}] {row[0].content}" for index, row in enumerate(rows))
        messages = [
            {"role": "system", "content": settings.system_prompt},
            {
                "role": "user",
                "content": (
                    f"请基于以下材料生成结构清晰的中文总结，包含主要结论和关键细节：\n{context_text}\n\n"
                    f"用户请求：{context.query}"
                ),
            },
        ]
        llm = get_llm_provider()
        answer = await llm.complete(messages)
        return AgentResult(
            answer=answer,
            agent_name=self.name,
            citations=build_citations(rows),
        )
