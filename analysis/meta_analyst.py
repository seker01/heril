"""LLM-powered diagnostic meta analysis over signals and factor summaries."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

import json


class TextGenerationClient(Protocol):
    """Protocol for FinGPT/GPT-style text completion."""

    def generate(self, prompt: str) -> str:
        """Generate a completion string."""


@dataclass(slots=True)
class MetaAnalyst:
    """Create structured diagnostics from recent signals with few-shot prompting."""

    llm_client: TextGenerationClient
    few_shot_examples: list[dict[str, str]] = field(default_factory=list)

    def build_prompt(self, recent_signals: list[dict[str, object]], factor_summary: dict[str, float]) -> str:
        """Build a prompt with few-shot examples and strict JSON schema request."""
        examples = "\n".join(
            f"Example Input: {e['input']}\nExample Output: {e['output']}" for e in self.few_shot_examples
        )
        return (
            "You are a quant diagnostics analyst. Return JSON list of objects with keys "
            "issue, suggestion, confidence.\n"
            f"{examples}\n"
            f"Signals: {json.dumps(recent_signals, default=str)}\n"
            f"Factor summary: {json.dumps(factor_summary)}\n"
        )

    def diagnose(self, recent_signals: list[dict[str, object]], factor_summary: dict[str, float]) -> list[dict[str, object]]:
        """Run LLM diagnostics and parse structured output."""
        prompt = self.build_prompt(recent_signals, factor_summary)
        response = self.llm_client.generate(prompt)
        parsed = json.loads(response)
        if not isinstance(parsed, list):
            raise ValueError("LLM response must be a list")
        for item in parsed:
            if not all(k in item for k in ("issue", "suggestion", "confidence")):
                raise ValueError("Malformed diagnostic item")
        return parsed
