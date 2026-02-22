"""Simple multi-source news collector with pluggable source adapters."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd


class SourceAdapter(Protocol):
    """Protocol for external source adapters."""

    def fetch(self) -> list[dict[str, str]]:
        """Return list of raw news items with fields: ticker, ts, title, body."""


@dataclass(slots=True)
class NewsScraper:
    """Aggregate raw news rows from multiple adapters."""

    adapters: list[SourceAdapter]

    def scrape(self) -> pd.DataFrame:
        """Collect and normalize source payloads into a DataFrame."""
        rows: list[dict[str, str]] = []
        for adapter in self.adapters:
            rows.extend(adapter.fetch())
        df = pd.DataFrame(rows)
        if df.empty:
            return pd.DataFrame(columns=["ticker", "timestamp", "text"])
        text = (df.get("title", "") + " " + df.get("body", "")).str.strip()
        return pd.DataFrame(
            {
                "ticker": df["ticker"],
                "timestamp": pd.to_datetime(df["ts"]),
                "text": text,
            }
        )
