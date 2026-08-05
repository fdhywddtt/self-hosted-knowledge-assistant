import redis.asyncio as aioredis


class EmbeddingCache:
    """Redis 缓存，连接失败时自动降级为不缓存，不影响主流程。"""

    def __init__(self, url: str):
        self._url = url
        self._client: aioredis.Redis | None = None

    async def _get_client(self) -> aioredis.Redis:
        if self._client is None:
            self._client = aioredis.from_url(self._url, decode_responses=True)
        return self._client

    async def mget(self, keys: list[str]) -> list[str | None]:
        try:
            client = await self._get_client()
            return await client.mget(keys)
        except Exception:
            return [None] * len(keys)

    async def mset(self, pairs: dict[str, str]) -> None:
        try:
            client = await self._get_client()
            await client.mset(pairs)
        except Exception:
            return
