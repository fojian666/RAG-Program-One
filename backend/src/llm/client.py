import json
from functools import lru_cache
from typing import Any

import httpx

from src.config.settings import Settings, get_settings


class LLMClient:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.api_key = self.settings.llm_api_key
        self.base_url = self.settings.llm_base_url.rstrip("/")
        self.model = self.settings.llm_model
        self.temperature = self.settings.llm_temperature
        self.max_tokens = self.settings.llm_max_tokens
        self.timeout = self.settings.llm_timeout

    def _ensure_key(self) -> None:
        if not self.api_key:
            raise ValueError("LLM_API_KEY is not configured")

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: dict[str, str] | None = None,
    ) -> str:
        self._ensure_key()

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def chat_structured(
        self,
        messages: list[dict[str, str]],
        output_schema: dict[str, Any],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        system_msg = (
            "You are a helpful assistant. "
            "Respond with valid JSON that matches the requested schema. "
            "Do not wrap the JSON in markdown code blocks."
        )
        # prepend system message if not present
        if not messages or messages[0].get("role") != "system":
            messages = [{"role": "system", "content": system_msg}, *messages]
        else:
            messages = [
                {
                    "role": "system",
                    "content": messages[0]["content"] + "\n" + system_msg,
                },
                *messages[1:],
            ]

        schema_prompt = (
            "\n\nRespond using this JSON schema:\n"
            f"{json.dumps(output_schema, indent=2, ensure_ascii=False)}"
        )
        messages[-1]["content"] += schema_prompt

        content = await self.chat(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        # strip markdown fences if any
        raw = content.strip()
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        return json.loads(raw.strip())


@lru_cache
def get_llm_client() -> LLMClient:
    return LLMClient()
