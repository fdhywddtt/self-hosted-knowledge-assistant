from abc import ABC, abstractmethod

from app.core.config import get_settings


def reciprocal_rank_fusion(rankings: list[list[str]], k: int = 60) -> dict[str, float]:
    """Reciprocal Rank Fusion，合并多个召回列表的排名。"""
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, item_id in enumerate(ranking, start=1):
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank)
    return scores


class Reranker(ABC):
    @abstractmethod
    async def rerank(self, query: str, items: list, top_k: int) -> list:
        ...


class IdentityReranker(Reranker):
    async def rerank(self, query: str, items: list, top_k: int) -> list:
        return items[:top_k]


class CrossEncoderReranker(Reranker):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self._model = None

    def _load(self):
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
            except ImportError as exc:
                raise RuntimeError("缺少 sentence-transformers，请安装 backend[local]") from exc
            self._model = CrossEncoder(self.model_name)
        return self._model

    async def rerank(self, query: str, items: list, top_k: int) -> list:
        model = self._load()
        pairs = [(query, item[0].content) for item in items]
        scores = model.predict(pairs)
        ranked = sorted(zip(items, scores), key=lambda pair: pair[1], reverse=True)
        return [item for item, _ in ranked[:top_k]]


def get_reranker() -> Reranker:
    settings = get_settings()
    if settings.reranker_provider == "cross-encoder":
        return CrossEncoderReranker(settings.cross_encoder_model)
    return IdentityReranker()
