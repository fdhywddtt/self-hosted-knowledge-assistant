import hashlib
import json

import httpx
import numpy as np
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import Settings, get_settings
from app.services.cache import EmbeddingCache


class OpenAIEmbeddingProvider:
    """OpenAI 兼容 Embedding 客户端，结果写入 Redis 缓存。"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._cache = EmbeddingCache(settings.redis_url)

    @retry(
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TransportError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def _embed_api(self, texts: list[str]) -> list[list[float]]:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.settings.embedding_base_url_final}/embeddings",
                headers={"Authorization": f"Bearer {self.settings.embedding_api_key or ''}"},
                json={"model": self.settings.embedding_model, "input": texts},
            )
            response.raise_for_status()
            data = response.json()
        return [item["embedding"] for item in data["data"]]

    async def embed(self, texts: list[str]) -> list[list[float]]:
        keys = [self._cache_key(text) for text in texts]
        cached = await self._cache.mget(keys)
        vectors: list[list[float]] = []
        missing_indexes: list[int] = []

        for index, raw in enumerate(cached):
            if raw is None:
                missing_indexes.append(index)
                vectors.append([])
            else:
                vectors.append(json.loads(raw))

        if missing_indexes:
            fresh = await self._embed_api([texts[index] for index in missing_indexes])
            self._validate_dimensions(fresh)
            await self._cache.mset({keys[index]: json.dumps(vector) for index, vector in zip(missing_indexes, fresh)})
            for index, vector in zip(missing_indexes, fresh):
                vectors[index] = vector

        return vectors

    def _validate_dimensions(self, vectors: list[list[float]]) -> None:
        expected = self.settings.embedding_dim
        for vector in vectors:
            if len(vector) != expected:
                raise ValueError(
                    f"Embedding 模型返回维度 {len(vector)}，与 EMBEDDING_DIM={expected} 不一致；"
                    "请修改配置后运行 python scripts/reembed_cli.py --recreate-table"
                )

    def _cache_key(self, text: str) -> str:
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return f"emb:{self.settings.embedding_model}:{digest}"


class DummyEmbeddingProvider:
    """确定性向量，用于离线测试与流程演示，不具备真实语义能力。"""

    def __init__(self, dim: int = 1536):
        self.dim = dim

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def _embed(self, text: str) -> list[float]:
        vector = np.zeros(self.dim, dtype=float)
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
            index = int(digest[:8], 16) % self.dim
            vector[index] += 1.0
        norm = float(np.linalg.norm(vector))
        if norm > 0:
            vector = vector / norm
        return vector.tolist()


def get_embedding_provider():
    settings = get_settings()
    if settings.embedding_provider == "dummy":
        return DummyEmbeddingProvider(settings.embedding_dim)
    if settings.embedding_provider == "openai":
        return OpenAIEmbeddingProvider(settings)
    raise ValueError(f"未知的 embedding provider: {settings.embedding_provider}")
