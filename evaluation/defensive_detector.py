"""Meta-learning detector for defensive/independent driver assets."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(slots=True)
class DefensiveAssetDetector:
    """Detect stocks repeatedly outperforming in market downturns."""

    lookback_events: int = 5
    outperformance_threshold: float = 0.02

    def detect(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return labels for assets that outperform during downturn windows.

        Required columns: ticker, market_return, stock_return
        """
        downturn = df[df["market_return"] < 0].copy()
        downturn["outperform"] = downturn["stock_return"] - downturn["market_return"]
        grp = downturn.groupby("ticker").agg(events=("ticker", "size"), mean_outperform=("outperform", "mean")).reset_index()
        grp = grp[(grp["events"] >= self.lookback_events) & (grp["mean_outperform"] >= self.outperformance_threshold)]
        grp["meta_label"] = "defensive_or_independent"
        return grp[["ticker", "meta_label", "events", "mean_outperform"]]
