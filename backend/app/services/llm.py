from abc import ABC, abstractmethod

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import Settings, get_settings


class LLMProvider(ABC):
    @abstractmethod
    async def complete(
        self,
        messages: list[dict],
        temperature: float | None = None,
        response_format: dict | None = None,
    ) -> str:
        ...


class OpenAILLMProvider(LLMProvider):
    def __init__(self, settings: Settings):
        self.settings = settings

    @retry(
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TransportError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def complete(
        self,
        messages: list[dict],
        temperature: float | None = None,
        response_format: dict | None = None,
    ) -> str:
        payload: dict = {
            "model": self.settings.llm_model,
            "messages": messages,
            "temperature": self.settings.llm_temperature if temperature is None else temperature,
        }
        if response_format:
            payload["response_format"] = response_format

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self.settings.llm_base_url_final}/chat/completions",
                headers={"Authorization": f"Bearer {self.settings.llm_api_key or ''}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        return data["choices"][0]["message"]["content"]


class DummyLLMProvider(LLMProvider):
    """离线演示用 Provider，不访问外部服务。"""

    async def complete(
        self,
        messages: list[dict],
        temperature: float | None = None,
        response_format: dict | None = None,
    ) -> str:
        if response_format:
            return '{"agent": "knowledge"}'
        return "（演示模式）这是基于知识库生成的回答。请配置真实的 LLM Provider 获取高质量回答。"


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    if settings.llm_provider == "dummy":
        return DummyLLMProvider()
    if settings.llm_provider == "openai":
        return OpenAILLMProvider(settings)
    raise ValueError(f"未知的 LLM provider: {settings.llm_provider}")
