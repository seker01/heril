from __future__ import annotations

from analysis.meta_analyst import MetaAnalyst


class DummyLLM:
    def generate(self, prompt: str) -> str:
        assert "Factor summary" in prompt
        return '[{"issue":"overfit sentiment","suggestion":"increase lookback","confidence":0.72}]'


def test_meta_analyst_structured_output() -> None:
    module = MetaAnalyst(llm_client=DummyLLM(), few_shot_examples=[{"input": "x", "output": "y"}])
    out = module.diagnose(
        recent_signals=[{"ticker": "ASELS", "alpha_score": 0.4}],
        factor_summary={"sentiment_score": 0.12},
    )
    assert out[0]["issue"] == "overfit sentiment"
