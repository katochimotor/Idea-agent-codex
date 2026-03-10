from __future__ import annotations

import json
import re

import httpx
from sqlmodel import Session

from backend.database.db import engine
from backend.services.provider_settings_service import ProviderSettingsService


class LLMClient:
    def __init__(self) -> None:
        self.provider_settings = ProviderSettingsService()

    def _fallback_response(self) -> dict:
        return {
            "title": "Автоматический исследователь пользовательских болей",
            "summary": "Сервис собирает обсуждения, выделяет боли и формирует готовые идеи продуктов.",
            "audience": "Indie hackers и product managers",
        }

    def _json_instruction(self, prompt: str) -> str:
        return (
            f"{prompt}\n\n"
            "Return only valid JSON with keys title, summary, audience. "
            "All values must be in Russian."
        )

    def _extract_json_object(self, raw_text: str) -> dict:
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not match:
            raise ValueError("Provider response does not contain JSON.")
        payload = json.loads(match.group(0))
        return {
            "title": payload.get("title", "").strip(),
            "summary": payload.get("summary", "").strip(),
            "audience": payload.get("audience", "").strip(),
        }

    def _extract_openai_text(self, response_json: dict) -> str:
        if response_json.get("output_text"):
            return response_json["output_text"]

        for item in response_json.get("output", []):
            for content in item.get("content", []):
                text_value = content.get("text")
                if isinstance(text_value, str) and text_value.strip():
                    return text_value
                if isinstance(text_value, dict) and text_value.get("value"):
                    return text_value["value"]
        raise ValueError("OpenAI response did not contain text output.")

    def _generate_openai(self, api_key: str, model_name: str, prompt: str) -> dict:
        response = httpx.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model_name,
                "instructions": "You generate concise Russian startup ideas.",
                "input": self._json_instruction(prompt),
                "max_output_tokens": 300,
            },
            timeout=45.0,
        )
        response.raise_for_status()
        return self._extract_json_object(self._extract_openai_text(response.json()))

    def _generate_anthropic(self, api_key: str, model_name: str, prompt: str) -> dict:
        response = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model_name,
                "system": "You generate concise Russian startup ideas.",
                "max_tokens": 300,
                "messages": [{"role": "user", "content": self._json_instruction(prompt)}],
            },
            timeout=45.0,
        )
        response.raise_for_status()
        text = "\n".join(
            block.get("text", "")
            for block in response.json().get("content", [])
            if block.get("type") == "text"
        )
        return self._extract_json_object(text)

    def generate_idea(self, prompt: str) -> dict:
        with Session(engine) as session:
            config = self.provider_settings.get_active_provider_config(session)

        if not config:
            return self._fallback_response()

        try:
            if config.provider == "openai":
                return self._generate_openai(config.api_key, config.model_name, prompt)
            if config.provider == "anthropic":
                return self._generate_anthropic(config.api_key, config.model_name, prompt)
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:400] if exc.response is not None else str(exc)
            raise RuntimeError(f"{config.provider} generation failed: {detail}") from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(f"{config.provider} generation failed: {exc}") from exc

        return self._fallback_response()
