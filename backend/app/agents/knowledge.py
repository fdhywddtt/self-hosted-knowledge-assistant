from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.core.config import get_settings
from app.services.citations import build_citations
from app.services.llm import get_llm_provider
from app.services.reranking import get_reranker
from app.services.retrieval import hybrid_search


class KnowledgeAgent(BaseAgent):
    name = "knowledge"
    description = "基于知识库回答事实性问题，适合查政策、流程、规格等"

    async def invoke(self, context: AgentContext) -> AgentResult:
        settings = get_settings()
        rows = await hybrid_search(context.session, context.query, document_id=context.document_id)
        reranker = get_reranker()
        rows = await reranker.rerank(context.query, rows, settings.rerank_top_k)

        if not rows:
            return AgentResult(
                answer="知识库中暂时没有找到相关内容，请上传相关文档后再试。",
                agent_name=self.name,
            )

        context_text = "\n\n".join(f"[材料 {index + 1}] {row[0].content}" for index, row in enumerate(rows))
        messages = [
            {"role": "system", "content": settings.system_prompt},
            {
                "role": "user",
                "content": (
                    f"参考材料：\n{context_text}\n\n问题：{context.query}\n\n"
                    "回答时在引用材料处标注 [1]、[2] 等编号。"
                ),
            },
        ]
        llm = get_llm_provider()
        answer = await llm.complete(messages)
        return AgentResult(
            answer=answer,
            agent_name=self.name,
            citations=build_citations(rows),
            metadata={"retrieved": len(rows)},
        )
