from __future__ import annotations

import json
import re

import requests

from clients.base import IntentClientError
from core.settings import get_settings


class OllamaIntentClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = self.settings.ollama_base_url.rstrip("/")
        self.model_name = self.settings.intent_model_name

    def classify(self, message: str) -> dict | None:
        prompt = self._build_prompt(message)
        content = self._request_ollama(prompt)
        return self._parse_json(content)

    def _request_ollama(self, prompt: str) -> str:
        chat_error = None
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                },
                timeout=self.settings.http_timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
            content = data.get("message", {}).get("content", "").strip()
            if content:
                return content
        except Exception as exc:
            chat_error = exc

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model_name, "prompt": prompt, "stream": False},
                timeout=self.settings.http_timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
            content = data.get("response", "").strip()
            if content:
                return content
        except Exception as exc:
            raise IntentClientError(f"Ollama unavailable: chat={chat_error}; generate={exc}") from exc

        raise IntentClientError("Ollama returned empty content")

    def _parse_json(self, content: str) -> dict | None:
        match = re.search(r"\{.*\}", content, flags=re.S)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

    def _build_prompt(self, message: str) -> str:
        return f"""
Classify the banking customer message into exactly one intent.
Allowed intents: check_balance, transfer_money, card_lost, loan_inquiry, transaction_history, account_support, unknown.
Return only JSON with keys: intent, confidence, reason.
Confidence must be a number from 0 to 1.
Message: {message}
""".strip()
