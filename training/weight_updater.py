"""Dynamic model weight update from LLM root-cause suggestions."""
from __future__ import annotations

from dataclasses import dataclass

from models.predictor import normalize_weights


@dataclass(slots=True)
class ReinforcementWeightUpdater:
    """Apply reinforcement logic to update feature weights."""

    eta: float = 0.15

    def apply(self, old_weights: dict[str, float], adjustments: dict[str, float]) -> dict[str, float]:
        """Update weights using additive learning rule then normalize."""
        merged = dict(old_weights)
        for factor, delta in adjustments.items():
            merged[factor] = merged.get(factor, 0.0) + self.eta * float(delta)
        return normalize_weights(merged)
