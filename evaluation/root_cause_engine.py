"""Root-cause analysis workflow for incorrect predictions."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from llm.ollama_client import OllamaClient

REQUIRED_KEYS = {
    "main_failure_reason",
    "missed_driver",
    "weak_signal",
    "overweighted_signal",
    "suggested_weight_adjustments",
    "confidence",
}


@dataclass(slots=True)
class RootCauseEngine:
    """Run local LLM diagnosis for wrong predictions."""

    llm_client: OllamaClient

    def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """Request structured failure analysis from local LLM."""
        system = (
            "You are a local quant root-cause engine. Return strictly valid JSON with keys: "
            "main_failure_reason, missed_driver, weak_signal, overweighted_signal, "
            "suggested_weight_adjustments, confidence."
        )
        user = f"Analyze this failed prediction context:\n{json.dumps(context, default=str)}"
        response = self.llm_client.generate_json(system, user)
        missing = REQUIRED_KEYS.difference(response.keys())
        if missing:
            raise ValueError(f"Missing keys in LLM response: {sorted(missing)}")
        response["confidence"] = float(response["confidence"])
        return response
