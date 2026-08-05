from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BASE_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "企业知识库智能问答助手"
    version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://assistant:assistant@localhost:5432/assistant"
    auto_create_tables: bool = False
    redis_url: str = "redis://localhost:6379/0"

    enable_auth: bool = False
    api_keys: Annotated[list[str], NoDecode] = []
    admin_api_keys: Annotated[list[str], NoDecode] = []
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "http://localhost:8080",
    ]

    storage_dir: str = str(ROOT_DIR / "data" / "documents")

    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536
    embedding_base_url: str | None = None
    embedding_api_key: str | None = None

    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str | None = None
    llm_api_key: str | None = None
    llm_temperature: float = 0.2

    chunk_size: int = 800
    chunk_overlap: int = 120
    top_k: int = 6
    rerank_top_k: int = 4
    reranker_provider: str = "rrf"
    cross_encoder_model: str = "BAAI/bge-reranker-base"

    system_prompt: str = (
        "你是一个严谨的企业知识库助手。只依据提供的材料回答，"
        "不要编造材料中不存在的信息；材料不足时明确说明。回答使用中文。"
    )

    @field_validator("api_keys", "admin_api_keys", "cors_origins", mode="before")
    @classmethod
    def split_list(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def embedding_base_url_final(self) -> str:
        return self.embedding_base_url or "https://api.openai.com/v1"

    @property
    def llm_base_url_final(self) -> str:
        return self.llm_base_url or "https://api.openai.com/v1"


@lru_cache
def get_settings() -> Settings:
    return Settings()
