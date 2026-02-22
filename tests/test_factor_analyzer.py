from __future__ import annotations

import pandas as pd

from analysis.factor_analyzer import FactorAnalyzer


def test_weight_update_clamps_and_normalizes() -> None:
    analyzer = FactorAnalyzer(eta=0.2)
    old = {
        "w_momentum": 0.2,
        "w_technical": 0.2,
        "w_volatility": 0.2,
        "w_macro": 0.2,
        "w_behavioral": 0.1,
        "w_sentiment": 0.1,
    }
    corr = {
        "momentum_score": 0.8,
        "technical_score": -1.0,
        "volatility_score": 0.1,
        "macro_score": 0.2,
        "behavioral_score": 0.0,
        "sentiment_score": 0.1,
    }
    new_weights = analyzer.update_weights(old, corr)
    assert all(0 <= v <= 1 for v in new_weights.values())
    assert abs(sum(new_weights.values()) - 1.0) < 1e-9
    assert new_weights["w_momentum"] > old["w_momentum"]


def test_generate_weight_rows() -> None:
    analyzer = FactorAnalyzer()
    df = pd.DataFrame(
        {
            "ticker": ["ASELS"] * 5,
            "regime": ["LowVol_Bull"] * 5,
            "momentum_score": [0.1, 0.2, 0.3, 0.4, 0.5],
            "technical_score": [0.0, 0.1, 0.0, 0.1, 0.0],
            "volatility_score": [0.2, 0.2, 0.2, 0.2, 0.2],
            "macro_score": [0.1, 0.2, 0.1, 0.2, 0.1],
            "behavioral_score": [0.0, 0.1, 0.0, 0.1, 0.0],
            "sentiment_score": [0.1, 0.2, 0.3, 0.4, 0.5],
            "forward_return_6m": [0.01, 0.02, 0.03, 0.04, 0.05],
        }
    )
    out = analyzer.generate_weight_rows(df, pd.DataFrame())
    assert out.shape[0] == 1
    assert out.iloc[0]["ticker"] == "ASELS"
