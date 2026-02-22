"""Simple local predictor model and dynamic weighting logic."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(slots=True)
class WeightedPredictor:
    """Linear weighted predictor for stock returns."""

    weights: dict[str, float]
    model_version: str = "v1-local"

    def predict(self, feature_row: pd.Series) -> tuple[float, str, float]:
        """Return predicted_return, direction, confidence."""
        score = 0.0
        for k, w in self.weights.items():
            score += float(feature_row.get(k, 0.0)) * float(w)
        direction = "UP" if score > 0.005 else "DOWN" if score < -0.005 else "FLAT"
        confidence = float(np.clip(abs(score) * 3.0, 0.0, 1.0))
        return float(score), direction, confidence


def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    """Clamp and normalize model weights."""
    cleaned = {k: float(np.clip(v, 0.0, 1.0)) for k, v in weights.items()}
    s = sum(cleaned.values())
    if s <= 0:
        n = max(1, len(cleaned))
        return {k: 1 / n for k in cleaned}
    return {k: v / s for k, v in cleaned.items()}
