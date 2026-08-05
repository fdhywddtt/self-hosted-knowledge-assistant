"""批量上传文档到运行中的后端服务。

用法: python scripts/ingest_cli.py ./docs ./guide.pdf --base-url http://localhost:8000
"""

import argparse
import asyncio
from pathlib import Path

import httpx


async def upload_file(
    client: httpx.AsyncClient,
    path: Path,
    base_url: str,
    api_key: str = "",
) -> None:
    headers = {"X-API-Key": api_key} if api_key else None
    with path.open("rb") as file_handle:
        response = await client.post(
            f"{base_url}/api/v1/documents/upload",
            files={"file": (path.name, file_handle)},
            headers=headers,
        )
    response.raise_for_status()
    data = response.json()
    print(f"已上传 {path.name} -> {data['id']} ({data['status']})")


async def main() -> None:
    parser = argparse.ArgumentParser(description="批量上传文档到知识库")
    parser.add_argument("paths", nargs="+", type=Path, help="文件或目录")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--api-key", default="", help="开启鉴权后的 API Key")
    args = parser.parse_args()

    files: list[Path] = [path for path in args.paths if path.is_file()]
    for path in args.paths:
        if path.is_dir():
            files.extend(item for item in path.rglob("*") if item.is_file())

    if not files:
        raise SystemExit("没有找到可上传的文件")

    base_url = args.base_url.rstrip("/")
    async with httpx.AsyncClient(timeout=120) as client:
        for path in files:
            await upload_file(client, path, base_url, args.api_key)


if __name__ == "__main__":
    asyncio.run(main())
