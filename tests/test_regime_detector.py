from __future__ import annotations

import numpy as np
import pandas as pd

from core.regime_detector import RegimeDetector


def test_regime_detector_labels() -> None:
    dates = pd.date_range("2024-01-01", periods=60, freq="D")
    df = pd.DataFrame(
        {
            "date": dates,
            "bist_close": np.concatenate([np.linspace(100, 80, 30), np.linspace(80, 100, 30)]),
            "market_vol": np.concatenate([np.full(30, 0.35), np.full(30, 0.15)]),
        }
    )
    detector = RegimeDetector(vol_threshold=0.25, trend_window=10)
    labels = detector.detect(df)

    assert "HighVol_Bear" in labels.values
    assert "LowVol_Bull" in labels.values
