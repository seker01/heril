"""Hybrid alpha score engine."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


FACTOR_COLUMNS = [
    "momentum_score",
    "technical_score",
    "volatility_score",
    "macro_score",
    "behavioral_score",
    "sentiment_score",
]


@dataclass(slots=True)
class HybridAlpha:
    """Compute hybrid alpha using adaptive weights."""

    pca_components: int = 3

    def normalize_factors(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize factors and project through PCA reconstruction."""
        out = df.copy()
        X = out[FACTOR_COLUMNS].fillna(0.0).to_numpy()
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        n_comp = min(self.pca_components, X_scaled.shape[1], max(1, X_scaled.shape[0]))
        pca = PCA(n_components=n_comp)
        X_pca = pca.fit_transform(X_scaled)
        X_recon = pca.inverse_transform(X_pca)
        out[FACTOR_COLUMNS] = X_recon
        return out

    @staticmethod
    def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
        """Clamp and normalize weights to sum to 1."""
        clipped = {k: min(1.0, max(0.0, float(v))) for k, v in weights.items()}
        total = sum(clipped.values())
        if total == 0:
            n = len(clipped)
            return {k: 1 / n for k in clipped}
        return {k: v / total for k, v in clipped.items()}

    def score_row(self, row: pd.Series, weights: dict[str, float]) -> float:
        """Compute weighted alpha score for a single row."""
        w = self.normalize_weights(weights)
        return float(sum(row[k] * w[f"w_{k.split('_score')[0]}"] for k in FACTOR_COLUMNS))

    def batch_score(self, factors_df: pd.DataFrame, weights_df: pd.DataFrame) -> pd.DataFrame:
        """Score each ticker-date in batch/backtest mode."""
        norm = self.normalize_factors(factors_df)
        merged = norm.merge(weights_df, on=["ticker", "regime"], how="left")
        merged = merged.fillna({
            "w_momentum": 1 / 6,
            "w_technical": 1 / 6,
            "w_volatility": 1 / 6,
            "w_macro": 1 / 6,
            "w_behavioral": 1 / 6,
            "w_sentiment": 1 / 6,
        })
        merged["alpha_score"] = merged.apply(
            lambda r: self.score_row(r, {
                "w_momentum": r["w_momentum"],
                "w_technical": r["w_technical"],
                "w_volatility": r["w_volatility"],
                "w_macro": r["w_macro"],
                "w_behavioral": r["w_behavioral"],
                "w_sentiment": r["w_sentiment"],
            }),
            axis=1,
        )
        return merged

    def online_score(self, row: pd.Series, weight_row: pd.Series) -> float:
        """Score one ticker-date in live mode."""
        return self.score_row(row, {
            "w_momentum": weight_row.get("w_momentum", 1 / 6),
            "w_technical": weight_row.get("w_technical", 1 / 6),
            "w_volatility": weight_row.get("w_volatility", 1 / 6),
            "w_macro": weight_row.get("w_macro", 1 / 6),
            "w_behavioral": weight_row.get("w_behavioral", 1 / 6),
            "w_sentiment": weight_row.get("w_sentiment", 1 / 6),
        })
