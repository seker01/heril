"""Feature engineering pipeline for market, technical, macro, and sentiment fields."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd

from db.repository import SQLRepository


TRADING_DAYS_MONTH = 21


@dataclass(slots=True)
class FeatureEngine:
    """Compute and persist feature rows aligned on rebalance dates."""

    repository: SQLRepository
    benchmark_ticker: str = "XU100"

    def load_prices(self, tickers: Iterable[str], start_date: str | None = None, end_date: str | None = None) -> pd.DataFrame:
        """Load OHLCV prices from database for requested tickers/date range."""
        params: dict[str, object] = {"tickers": list(tickers)}
        where = ["ticker = ANY(:tickers)"]
        if start_date:
            where.append("date >= :start_date")
            params["start_date"] = start_date
        if end_date:
            where.append("date <= :end_date")
            params["end_date"] = end_date
        sql = f"""
            SELECT ticker, date, open, high, low, close, volume
            FROM prices
            WHERE {' AND '.join(where)}
            ORDER BY ticker, date
        """
        df = self.repository.fetch_df(sql, params)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
        return df

    def compute_features(self, prices: pd.DataFrame, macro: pd.DataFrame, sentiment: pd.DataFrame, rebalance_dates: pd.DatetimeIndex) -> pd.DataFrame:
        """Compute all features and return only rebalance rows."""
        if prices.empty:
            return pd.DataFrame()

        frames: list[pd.DataFrame] = []
        benchmark = prices.loc[prices["ticker"] == self.benchmark_ticker, ["date", "close"]].rename(columns={"close": "benchmark_close"})
        benchmark["benchmark_ret"] = benchmark["benchmark_close"].pct_change()

        for ticker, tdf in prices.groupby("ticker", sort=False):
            tdf = tdf.sort_values("date").merge(benchmark[["date", "benchmark_close", "benchmark_ret"]], on="date", how="left")
            tdf["ret_1d"] = tdf["close"].pct_change()
            tdf["momentum_3m"] = tdf["close"].pct_change(TRADING_DAYS_MONTH * 3)
            tdf["momentum_6m"] = tdf["close"].pct_change(TRADING_DAYS_MONTH * 6)
            tdf["momentum_12m"] = tdf["close"].pct_change(TRADING_DAYS_MONTH * 12)
            tdf["rsi"] = self._rsi(tdf["close"], window=14)
            macd_line = self._ema(tdf["close"], 12) - self._ema(tdf["close"], 26)
            tdf["macd_slope"] = macd_line.diff(5)
            tdf["adx"] = self._adx(tdf)
            tdf["volatility_30d"] = tdf["ret_1d"].rolling(30).std() * np.sqrt(252)
            tdf["vol_compression"] = tdf["volatility_30d"] / tdf["volatility_30d"].rolling(90).mean()
            tdf["relative_strength"] = (tdf["close"] / tdf["benchmark_close"]).pct_change(TRADING_DAYS_MONTH * 3)
            tdf["beta"] = (
                tdf["ret_1d"].rolling(60).cov(tdf["benchmark_ret"]) /
                (tdf["benchmark_ret"].rolling(60).var())
            )
            tdf["ticker"] = ticker
            frames.append(tdf)

        feat = pd.concat(frames, ignore_index=True)
        feat = feat.merge(macro, on="date", how="left")
        feat = feat.merge(sentiment, on=["ticker", "date"], how="left")
        feat = feat[feat["date"].isin(rebalance_dates)]
        feat = feat[[
            "ticker", "date", "momentum_3m", "momentum_6m", "momentum_12m",
            "rsi", "macd_slope", "adx", "volatility_30d", "vol_compression",
            "relative_strength", "beta", "macro_regime", "market_breadth",
            "sentiment_score", "sentiment_momentum", "sentiment_surprise", "news_volume",
        ]]
        return feat.replace([np.inf, -np.inf], np.nan).fillna(method="ffill").fillna(0.0)

    def save_features(self, features: pd.DataFrame) -> None:
        """Persist computed features."""
        self.repository.upsert_df("features", features)

    @staticmethod
    def _ema(series: pd.Series, span: int) -> pd.Series:
        return series.ewm(span=span, adjust=False).mean()

    @staticmethod
    def _rsi(close: pd.Series, window: int = 14) -> pd.Series:
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(window).mean()
        loss = -delta.clip(upper=0).rolling(window).mean()
        rs = gain / loss.replace(0, np.nan)
        return 100 - (100 / (1 + rs))

    @staticmethod
    def _adx(df: pd.DataFrame, window: int = 14) -> pd.Series:
        up_move = df["high"].diff()
        down_move = -df["low"].diff()
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
        tr = pd.concat([
            (df["high"] - df["low"]),
            (df["high"] - df["close"].shift()).abs(),
            (df["low"] - df["close"].shift()).abs(),
        ], axis=1).max(axis=1)
        atr = tr.rolling(window).mean()
        plus_di = 100 * pd.Series(plus_dm, index=df.index).rolling(window).sum() / atr
        minus_di = 100 * pd.Series(minus_dm, index=df.index).rolling(window).sum() / atr
        dx = ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)) * 100
        return dx.rolling(window).mean()


def build_rebalance_dates(prices: pd.DataFrame, freq: str = "M") -> pd.DatetimeIndex:
    """Construct rebalance schedule from available price history."""
    if prices.empty:
        return pd.DatetimeIndex([])
    return pd.DatetimeIndex(sorted(pd.to_datetime(prices["date"]).dt.to_period(freq).dt.end_time.unique()))
