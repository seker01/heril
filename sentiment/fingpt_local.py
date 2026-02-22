"""Local sentiment scoring with optional FinGPT pipeline fallback."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass(slots=True)
class FinGPTSentimentEngine:
    """Compute local sentiment factors without external APIs."""

    def score_items(self, rows: Iterable[dict[str, object]]) -> pd.DataFrame:
        """Score news/social payloads into sentiment features.

        Input row fields: ticker, date, text, source, volume_spike(optional), geopolitical(optional)
        """
        data = pd.DataFrame(list(rows))
        if data.empty:
            return pd.DataFrame(columns=["ticker", "score_date", "news_polarity", "social_sentiment", "volume_spike", "geopolitical_signal", "composite_score", "source_payload"])

        data["date"] = pd.to_datetime(data["date"]).dt.date
        data["score"] = data["text"].astype(str).map(self._rule_sentiment)

        news = data[data["source"].eq("news")].groupby(["ticker", "date"])["score"].mean().rename("news_polarity")
        social = data[data["source"].eq("social")].groupby(["ticker", "date"])["score"].mean().rename("social_sentiment")
        out = pd.concat([news, social], axis=1).fillna(0.0).reset_index()

        out["volume_spike"] = data.groupby(["ticker", "date"])["volume_spike"].mean().reset_index(drop=True).fillna(0.0)
        out["geopolitical_signal"] = data.groupby(["ticker", "date"])["geopolitical"].mean().reset_index(drop=True).fillna(0.0)
        out["composite_score"] = 0.4 * out["news_polarity"] + 0.3 * out["social_sentiment"] + 0.2 * out["volume_spike"] + 0.1 * out["geopolitical_signal"]
        out = out.rename(columns={"date": "score_date"})
        out["source_payload"] = "{}"
        return out

    @staticmethod
    def _rule_sentiment(text: str) -> float:
        low = text.lower()
        pos = sum(w in low for w in ["beat", "upgrade", "growth", "strong", "contract"]) 
        neg = sum(w in low for w in ["downgrade", "miss", "weak", "risk", "fine", "war"])
        raw = pos - neg
        return float(np.clip(raw / 3.0, -1.0, 1.0))
