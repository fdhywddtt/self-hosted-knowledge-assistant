from app.schemas.chat import Citation


def build_citations(rows) -> list[Citation]:
    citations: list[Citation] = []
    for rank, (chunk, document) in enumerate(rows, start=1):
        citations.append(
            Citation(
                chunk_id=chunk.id,
                document_id=document.id,
                filename=document.filename,
                page_number=chunk.page_number,
                excerpt=chunk.content[:500],
                score=round(1.0 / rank, 4),
            )
        )
    return citations
