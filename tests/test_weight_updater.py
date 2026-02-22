from __future__ import annotations

from training.weight_updater import ReinforcementWeightUpdater


def test_weight_updater_normalized() -> None:
    updater = ReinforcementWeightUpdater(eta=0.2)
    old = {"momentum": 0.3, "technical": 0.2, "sentiment": 0.5}
    adj = {"momentum": 0.4, "technical": -0.5, "sentiment": 0.1}
    new = updater.apply(old, adj)
    assert abs(sum(new.values()) - 1.0) < 1e-8
    assert all(0 <= v <= 1 for v in new.values())
