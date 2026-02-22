"""Telegram markdown reporting for daily alpha outputs."""
from __future__ import annotations

from dataclasses import dataclass

import requests
import pandas as pd


@dataclass(slots=True)
class TelegramReporter:
    """Publish daily summary report to Telegram channel."""

    bot_token: str
    chat_id: str
    timeout: int = 20

    def format_report(self, signals_df: pd.DataFrame, diagnostics: list[dict[str, object]]) -> str:
        """Compose Markdown message body."""
        lines = ["*Hybrid Alpha Daily Report*", ""]
        for row in signals_df.sort_values("alpha_score", ascending=False).head(10).itertuples(index=False):
            lines.append(
                f"- `{row.ticker}` | alpha: *{row.alpha_score:.3f}* | regime: `{row.regime}` | "
                f"sent: {getattr(row, 'sentiment_score', 0):.2f}"
            )
        lines.append("\n*Meta Diagnostics*")
        for d in diagnostics:
            lines.append(f"- Issue: {d['issue']} | Suggestion: {d['suggestion']} | Conf: {d['confidence']}")
        return "\n".join(lines)

    def send_report(self, markdown_text: str) -> dict[str, object]:
        """Send message to telegram bot API."""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": markdown_text, "parse_mode": "Markdown"}
        resp = requests.post(url, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()
