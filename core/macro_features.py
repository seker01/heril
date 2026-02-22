"""Macro feature generation utilities."""
from __future__ import annotations

import pandas as pd


def compute_macro_regime(bist: pd.Series, usdtry: pd.Series, y2: pd.Series, dates: pd.Series) -> pd.DataFrame:
    """Compute macro regime and market breadth proxy from major macro time series."""
    df = pd.DataFrame({"date": pd.to_datetime(dates), "bist": bist, "usdtry": usdtry, "y2": y2}).sort_values("date")
    bist_trend = df["bist"].pct_change(20)
    fx_trend = df["usdtry"].pct_change(20)
    yield_trend = df["y2"].diff(20)

    def regime(i: int) -> str:
        if bist_trend.iloc[i] > 0 and fx_trend.iloc[i] < 0 and yield_trend.iloc[i] <= 0:
            return "RiskOn"
        if bist_trend.iloc[i] < 0 and (fx_trend.iloc[i] > 0 or yield_trend.iloc[i] > 0):
            return "RiskOff"
        return "Neutral"

    df["macro_regime"] = [regime(i) if i >= 20 else "Neutral" for i in range(len(df))]
    df["market_breadth"] = (bist_trend - fx_trend).fillna(0.0)
    return df[["date", "macro_regime", "market_breadth"]]
