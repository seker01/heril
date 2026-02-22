from __future__ import annotations

from evaluation.root_cause_engine import RootCauseEngine


class DummyLLM:
    model = "llama3"

    def generate_json(self, system_prompt: str, user_prompt: str):
        return {
            "main_failure_reason": "macro shock",
            "missed_driver": "rate surprise",
            "weak_signal": "momentum",
            "overweighted_signal": "sentiment",
            "suggested_weight_adjustments": {"macro": 0.3, "sentiment": -0.2},
            "confidence": 0.81,
        }


def test_root_cause_json_contract() -> None:
    engine = RootCauseEngine(llm_client=DummyLLM())
    out = engine.analyze({"a": 1})
    assert out["confidence"] > 0
    assert "suggested_weight_adjustments" in out
