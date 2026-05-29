from __future__ import annotations

import requests

from app.clients.base import ExternalServiceError
from app.core.settings import get_settings


class OllamaClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = self.settings.ollama_base_url.rstrip("/")
        self.model_name = self.settings.intent_model_name

    def generate(self, prompt: str) -> str:
        chat_error = None
        try:
            return self._call_chat(prompt)
        except Exception as exc:
            chat_error = exc

        try:
            return self._call_generate(prompt)
        except Exception as exc:
            raise ExternalServiceError(
                f"Ollama /api/chat failed: {chat_error}; /api/generate failed: {exc}"
            ) from exc

    def _call_chat(self, prompt: str) -> str:
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=self.settings.http_timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        content = data.get("message", {}).get("content", "").strip()
        if not content:
            raise ExternalServiceError("Ollama /api/chat returned an empty response")
        return content

    def _call_generate(self, prompt: str) -> str:
        payload = {"model": self.model_name, "prompt": prompt, "stream": False}
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=self.settings.http_timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        content = data.get("response", "").strip()
        if not content:
            raise ExternalServiceError("Ollama /api/generate returned an empty response")
        return content
