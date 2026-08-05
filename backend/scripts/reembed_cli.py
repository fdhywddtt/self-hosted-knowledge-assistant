"""更换 Embedding 模型后重建全部向量。

用法:
  python scripts/reembed_cli.py                    # 同维度模型切换，清空并重建向量
  python scripts/reembed_cli.py --recreate-table   # 模型维度变化时按新维度重建 chunks 表
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import delete, select, text

from app.db.base import Base
from app.db.models import Chunk, Document
from app.db.session import SessionLocal, engine
from app.services.ingestion import ingest_document


async def recreate_chunks_table() -> None:
    async with engine.begin() as connection:
        await connection.execute(text("DROP TABLE IF EXISTS chunks CASCADE"))
        await connection.run_sync(Base.metadata.create_all)


async def run(recreate_table: bool) -> None:
    if recreate_table:
        print("正在按当前 EMBEDDING_DIM 重建 chunks 表...")
        await recreate_chunks_table()

    async with SessionLocal() as session:
        await session.execute(delete(Chunk))
        documents = (
            await session.execute(select(Document).where(Document.status.in_(["ready", "failed"])))
        ).scalars().all()
        await session.commit()

    print(f"共 {len(documents)} 篇文档需要重新向量化")
    for document in documents:
        print(f"处理: {document.filename}")
        await ingest_document(document.id)
    print("重建完成，请在前端或 API 中检查文档状态")


def main() -> None:
    parser = argparse.ArgumentParser(description="重建知识库向量")
    parser.add_argument(
        "--recreate-table",
        action="store_true",
        help="按新维度重建 chunks 表，维度未变化时不需要",
    )
    args = parser.parse_args()
    asyncio.run(run(args.recreate_table))


if __name__ == "__main__":
    main()
