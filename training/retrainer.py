"""Periodic local retraining hooks."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from models.predictor import normalize_weights


@dataclass(slots=True)
class PeriodicRetrainer:
    """Retrain simple weighted model from historical factor-outcome data."""

    min_rows: int = 50

    def retrain_weights(self, train_df: pd.DataFrame, feature_cols: list[str], target_col: str = "actual_return") -> dict[str, float]:
        """Fit robust correlation-based weights for local deployment."""
        if train_df.shape[0] < self.min_rows:
            base = {c: 1 / len(feature_cols) for c in feature_cols}
            return normalize_weights(base)

        corr = {}
        for col in feature_cols:
            v = train_df[[col, target_col]].corr().iloc[0, 1]
            corr[col] = max(0.0, abs(float(0 if pd.isna(v) else v)))
        return normalize_weights(corr)
