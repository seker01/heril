from __future__ import annotations

import pandas as pd

from evaluation.defensive_detector import DefensiveAssetDetector


def test_detect_defensive_assets() -> None:
    df = pd.DataFrame(
        {
            "ticker": ["AAA"] * 6 + ["BBB"] * 6,
            "market_return": [-0.03, -0.02, -0.01, -0.04, -0.02, -0.01] * 2,
            "stock_return": [0.01, 0.0, 0.02, 0.01, 0.0, 0.01, -0.02, -0.03, -0.01, -0.01, -0.02, -0.04],
        }
    )
    detector = DefensiveAssetDetector(lookback_events=5, outperformance_threshold=0.015)
    out = detector.detect(df)
    assert "AAA" in out["ticker"].values
    assert "BBB" not in out["ticker"].values
