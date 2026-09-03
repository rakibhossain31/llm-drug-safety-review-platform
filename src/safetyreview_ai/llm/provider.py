from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

from safetyreview_ai.core.config import get_settings


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError


class DeterministicFallbackProvider(LLMProvider):
    name = "deterministic-fallback"

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        return json.dumps(
            {
                "provider": self.name,
                "message": "Deterministic fallback active; structured PV modules produced the result.",
            }
        )


class OpenAICompatibleProvider(LLMProvider):
    name = "openai-compatible"

    def __init__(self) -> None:
        settings = get_settings()
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install requirements.txt to enable the optional OpenAI provider.") from exc
        self.client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
        self.model = settings.openai_model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    if settings.openai_api_key:
        try:
            return OpenAICompatibleProvider()
        except Exception:
            return DeterministicFallbackProvider()
    return DeterministicFallbackProvider()
