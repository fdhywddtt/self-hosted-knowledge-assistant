from uuid import UUID

from sqlalchemy import func, select

from app.core.config import get_settings
from app.db.models import Chunk, Document
from app.services.embeddings import get_embedding_provider
from app.services.reranking import reciprocal_rank_fusion


async def hybrid_search(session, query: str, top_k: int | None = None, document_id: UUID | None = None):
    """向量检索 + PostgreSQL 全文检索，再用 RRF 融合。"""
    settings = get_settings()
    top_k = top_k or settings.top_k
    provider = get_embedding_provider()
    query_vector = (await provider.embed([query]))[0]

    conditions = [Document.status == "ready"]
    if document_id:
        conditions.append(Chunk.document_id == document_id)

    vector_statement = (
        select(Chunk, Document)
        .join(Document, Chunk.document_id == Document.id)
        .where(*conditions)
        .order_by(Chunk.embedding.cosine_distance(query_vector))
        .limit(top_k * 4)
    )
    vector_rows = (await session.execute(vector_statement)).all()
    vector_ranking = [str(row[0].id) for row in vector_rows]

    keyword_statement = (
        select(Chunk, Document)
        .join(Document, Chunk.document_id == Document.id)
        .where(
            *conditions,
            func.to_tsvector("simple", Chunk.content).op("@@")(func.plainto_tsquery("simple", query)),
        )
        .limit(top_k * 4)
    )
    keyword_rows = (await session.execute(keyword_statement)).all()
    keyword_ranking = [str(row[0].id) for row in keyword_rows]

    fused_scores = reciprocal_rank_fusion([vector_ranking, keyword_ranking])
    ordered_ids = sorted(fused_scores, key=fused_scores.get, reverse=True)[:top_k]
    rows_by_id = {str(row[0].id): row for row in [*vector_rows, *keyword_rows]}
    return [rows_by_id[chunk_id] for chunk_id in ordered_ids if chunk_id in rows_by_id]
