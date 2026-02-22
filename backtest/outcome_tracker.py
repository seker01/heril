"""Signal outcome tracking for forward performance labels."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(slots=True)
class OutcomeTracker:
    """Compute 3m/6m returns, drawdown and realized vol."""

    success_threshold: float = 0.10

    def evaluate_signal(self, signal_date: pd.Timestamp, price_series: pd.Series) -> dict[str, float | bool]:
        """Evaluate a single signal given close prices indexed by date."""
        if signal_date not in price_series.index:
            raise ValueError("signal_date missing in price series")

        start_px = float(price_series.loc[signal_date])
        fwd_3m = self._fwd_return(price_series, signal_date, 63, start_px)
        fwd_6m = self._fwd_return(price_series, signal_date, 126, start_px)

        window = price_series.loc[signal_date:].head(126)
        running_max = window.cummax()
        drawdown = (window / running_max - 1.0).min() if len(window) else 0.0
        rets = window.pct_change().dropna()
        vol = float(rets.std() * np.sqrt(252)) if not rets.empty else 0.0

        return {
            "return_3m": float(fwd_3m),
            "return_6m": float(fwd_6m),
            "max_drawdown": float(drawdown),
            "volatility": vol,
            "success_label": bool(fwd_6m > self.success_threshold),
        }

    @staticmethod
    def _fwd_return(price_series: pd.Series, signal_date: pd.Timestamp, horizon: int, start_px: float) -> float:
        future = price_series.loc[signal_date:].head(horizon + 1)
        if len(future) < horizon + 1:
            return np.nan
        end_px = float(future.iloc[-1])
        return end_px / start_px - 1.0

    def run_backtest(self, signals_df: pd.DataFrame, prices_df: pd.DataFrame) -> pd.DataFrame:
        """Compute outcomes for all provided signals."""
        out: list[dict[str, float | bool | int]] = []
        px_map = {
            t: g.sort_values("date").set_index(pd.to_datetime(g["date"]))["close"]
            for t, g in prices_df.groupby("ticker")
        }
        for row in signals_df.itertuples(index=False):
            res = self.evaluate_signal(pd.to_datetime(row.date), px_map[row.ticker])
            res["signal_id"] = row.id
            out.append(res)
        return pd.DataFrame(out)
