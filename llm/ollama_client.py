"""Local Ollama client for structured JSON generation."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(slots=True)
class OllamaClient:
    """HTTP client for local Ollama inference."""

    base_url: str = "http://127.0.0.1:11434"
    model: str = "llama3"

    @classmethod
    def from_env(cls) -> "OllamaClient":
        return cls(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
            model=os.getenv("LLM_MODEL", "llama3"),
        )

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        """Generate JSON response from local model and parse safely."""
        payload = {
            "model": self.model,
            "format": "json",
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        resp = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=60)
        resp.raise_for_status()
        content = resp.json().get("message", {}).get("content", "{}")
        return json.loads(content)
