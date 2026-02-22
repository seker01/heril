from __future__ import annotations

import pandas as pd

from telegram.reporter import TelegramReporter


class DummyResponse:
    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, object]:
        return {"ok": True}


def test_send_report(monkeypatch) -> None:
    reporter = TelegramReporter(bot_token="token", chat_id="chat")

    def fake_post(url: str, json: dict[str, object], timeout: int):
        assert "sendMessage" in url
        assert json["chat_id"] == "chat"
        return DummyResponse()

    monkeypatch.setattr("telegram.reporter.requests.post", fake_post)
    payload = reporter.send_report("*hello*")
    assert payload["ok"] is True


def test_format_report() -> None:
    reporter = TelegramReporter(bot_token="token", chat_id="chat")
    signals = pd.DataFrame([{"ticker": "ASELS", "alpha_score": 0.55, "regime": "LowVol_Bull", "sentiment_score": 0.3}])
    txt = reporter.format_report(signals, [{"issue": "late macro", "suggestion": "add nowcast", "confidence": 0.8}])
    assert "ASELS" in txt
    assert "Meta Diagnostics" in txt
