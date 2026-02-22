"""Sentiment classification and daily aggregation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd


class LLMClient(Protocol):
    """LLM protocol for sentiment + event extraction."""

    def classify(self, text: str) -> dict[str, object]:
        """Return payload with sentiment in {-1,0,1} and event flags list."""


@dataclass(slots=True)
class RuleBasedLLM:
    """Fallback deterministic sentiment classifier for tests/offline usage."""

    positive_tokens: tuple[str, ...] = ("strong", "growth", "win", "contract", "upgrade")
    negative_tokens: tuple[str, ...] = ("loss", "downgrade", "penalty", "risk", "lawsuit")

    def classify(self, text: str) -> dict[str, object]:
        low = text.lower()
        score = 0
        if any(t in low for t in self.positive_tokens):
            score += 1
        if any(t in low for t in self.negative_tokens):
            score -= 1
        flags = [k for k in ["earnings", "contracts", "regulation", "geopolitics"] if k in low]
        return {"sentiment": max(-1, min(1, score)), "event_flags": flags}


@dataclass(slots=True)
class SentimentEngine:
    """Classify scraped news and derive daily sentiment features."""

    llm_client: LLMClient

    def classify_news(self, news_df: pd.DataFrame) -> pd.DataFrame:
        """Classify each news row into sentiment and event flags."""
        if news_df.empty:
            return pd.DataFrame(columns=["ticker", "date", "sentiment", "event_flags"])

        rows: list[dict[str, object]] = []
        for r in news_df.itertuples(index=False):
            prediction = self.llm_client.classify(r.text)
            rows.append(
                {
                    "ticker": r.ticker,
                    "date": pd.to_datetime(r.timestamp).normalize(),
                    "sentiment": float(prediction["sentiment"]),
                    "event_flags": prediction.get("event_flags", []),
                }
            )
        return pd.DataFrame(rows)

    def aggregate_daily(self, classified_df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate daily sentiment_score/momentum/surprise/news_volume."""
        if classified_df.empty:
            return pd.DataFrame(columns=["ticker", "date", "sentiment_score", "sentiment_momentum", "sentiment_surprise", "news_volume"])
        agg = (
            classified_df.groupby(["ticker", "date"], as_index=False)
            .agg(sentiment_score=("sentiment", "mean"), news_volume=("sentiment", "size"))
            .sort_values(["ticker", "date"])
        )
        agg["sentiment_momentum"] = agg.groupby("ticker")["sentiment_score"].transform(lambda s: s.rolling(5, min_periods=1).mean())
        long_avg = agg.groupby("ticker")["sentiment_score"].transform(lambda s: s.rolling(30, min_periods=1).mean())
        agg["sentiment_surprise"] = agg["sentiment_score"] - long_avg
        return agg
