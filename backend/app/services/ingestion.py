import uuid
from pathlib import Path

from app.core.config import get_settings
from app.db.models import Chunk, Document
from app.db.session import SessionLocal
from app.services.embeddings import get_embedding_provider
from app.services.parsing import SUPPORTED_EXTENSIONS, parse_document


def save_upload(file_bytes: bytes, filename: str) -> tuple[Path, str]:
    settings = get_settings()
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"不支持的文件类型: {extension}")

    storage_dir = Path(settings.storage_dir)
    storage_dir.mkdir(parents=True, exist_ok=True)
    target = storage_dir / f"{uuid.uuid4().hex}{extension}"
    target.write_bytes(file_bytes)
    return target, str(target)


async def ingest_document(document_id: uuid.UUID) -> None:
    """后台任务：解析、分块、向量化并写入 chunks 表。"""
    settings = get_settings()
    async with SessionLocal() as session:
        document = await session.get(Document, document_id)
        if document is None:
            return

        try:
            document.status = "processing"
            await session.commit()

            parsed = parse_document(document.storage_path)
            if not parsed.chunks:
                raise ValueError("文档解析后没有可用文本")

            provider = get_embedding_provider()
            embeddings = await provider.embed([item.content for item in parsed.chunks])
            for item, embedding in zip(parsed.chunks, embeddings):
                session.add(
                    Chunk(
                        document_id=document.id,
                        content=item.content,
                        embedding=embedding,
                        page_number=item.page_number,
                    )
                )

            document.status = "ready"
            document.error = None
        except Exception as exc:
            document.status = "failed"
            document.error = str(exc)

        await session.commit()
