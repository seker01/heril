"""Factor importance and adaptive weight updates."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

WEIGHT_MAP = {
    "momentum_score": "w_momentum",
    "technical_score": "w_technical",
    "volatility_score": "w_volatility",
    "macro_score": "w_macro",
    "behavioral_score": "w_behavioral",
    "sentiment_score": "w_sentiment",
}


@dataclass(slots=True)
class FactorAnalyzer:
    """Estimate factor value and update weights using Bayesian soft step."""

    eta: float = 0.1

    def correlations(self, df: pd.DataFrame, target: str = "forward_return_6m") -> dict[str, float]:
        """Compute Pearson correlation between each factor and forward return."""
        corr: dict[str, float] = {}
        for factor in WEIGHT_MAP:
            value = df[[factor, target]].corr().iloc[0, 1]
            corr[factor] = 0.0 if pd.isna(value) else float(value)
        return corr

    def update_weights(self, old_weights: dict[str, float], corr: dict[str, float]) -> dict[str, float]:
        """Apply soft update, clamp to [0,1], normalize sum=1."""
        updated = {}
        for factor, weight_name in WEIGHT_MAP.items():
            prior = float(old_weights.get(weight_name, 1 / len(WEIGHT_MAP)))
            posterior = prior + self.eta * float(corr.get(factor, 0.0))
            updated[weight_name] = float(np.clip(posterior, 0.0, 1.0))
        total = sum(updated.values())
        if total <= 0:
            n = len(updated)
            return {k: 1 / n for k in updated}
        return {k: v / total for k, v in updated.items()}

    def generate_weight_rows(self, df: pd.DataFrame, weights_df: pd.DataFrame) -> pd.DataFrame:
        """Build updated weights per (ticker, regime) slice."""
        rows: list[dict[str, object]] = []
        has_cols = {"ticker", "regime"}.issubset(set(weights_df.columns))
        for (ticker, regime), slice_df in df.groupby(["ticker", "regime"]):
            corr = self.correlations(slice_df)
            if has_cols:
                base = weights_df[(weights_df["ticker"] == ticker) & (weights_df["regime"] == regime)]
                old = base.iloc[0].to_dict() if not base.empty else {}
            else:
                old = {}
            new_w = self.update_weights(old, corr)
            rows.append({"ticker": ticker, "regime": regime, **new_w, "last_updated": pd.Timestamp.utcnow().date()})
        return pd.DataFrame(rows)
