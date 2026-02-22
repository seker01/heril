"""Market regime detection."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(slots=True)
class RegimeDetector:
    """Rule-based regime detector."""

    vol_threshold: float = 0.25
    trend_window: int = 20

    def detect(self, market_df: pd.DataFrame) -> pd.Series:
        """Return regime labels for each row in market dataframe.

        Required columns: date, bist_close, market_vol.
        """
        df = market_df.sort_values("date").copy()
        df["trend"] = df["bist_close"] / df["bist_close"].shift(self.trend_window) - 1

        def classify(row: pd.Series) -> str:
            if row["market_vol"] > self.vol_threshold and row["trend"] < 0:
                return "HighVol_Bear"
            if row["market_vol"] <= self.vol_threshold and row["trend"] > 0:
                return "LowVol_Bull"
            return "Sideways"

        return df.apply(classify, axis=1)
