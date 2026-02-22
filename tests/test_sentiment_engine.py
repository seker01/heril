from __future__ import annotations

import pandas as pd

from sentiment.engine import RuleBasedLLM, SentimentEngine


def test_sentiment_aggregation_metrics() -> None:
    engine = SentimentEngine(llm_client=RuleBasedLLM())
    news_df = pd.DataFrame(
        {
            "ticker": ["ASELS", "ASELS", "ASELS", "SISE"],
            "timestamp": pd.to_datetime(["2024-01-02 09:00", "2024-01-02 13:00", "2024-01-03 09:00", "2024-01-03 10:00"]),
            "text": [
                "Company reports strong earnings growth",
                "New contract win announced",
                "Regulation risk and lawsuit concerns",
                "Neutral operations update",
            ],
        }
    )
    classified = engine.classify_news(news_df)
    agg = engine.aggregate_daily(classified)

    asels_day1 = agg[(agg["ticker"] == "ASELS") & (agg["date"] == pd.Timestamp("2024-01-02"))].iloc[0]
    assert asels_day1["news_volume"] == 2
    assert asels_day1["sentiment_score"] > 0

    asels_day2 = agg[(agg["ticker"] == "ASELS") & (agg["date"] == pd.Timestamp("2024-01-03"))].iloc[0]
    assert asels_day2["sentiment_score"] < 0
    assert "sentiment_surprise" in agg.columns
