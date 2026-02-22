"""Example entrypoint wiring all modules together."""
from __future__ import annotations

from db.connection import get_engine
from db.repository import SQLRepository
from core.feature_engine import FeatureEngine
from core.regime_detector import RegimeDetector
from core.alpha_engine import HybridAlpha
from backtest.outcome_tracker import OutcomeTracker
from analysis.factor_analyzer import FactorAnalyzer
from core.pipeline import ResearchPipeline


def build_pipeline() -> ResearchPipeline:
    repo = SQLRepository(engine=get_engine())
    return ResearchPipeline(
        repository=repo,
        feature_engine=FeatureEngine(repository=repo),
        regime_detector=RegimeDetector(),
        alpha_engine=HybridAlpha(),
        outcome_tracker=OutcomeTracker(),
        factor_analyzer=FactorAnalyzer(),
    )


if __name__ == "__main__":
    pipeline = build_pipeline()
    print(f"Pipeline ready: {pipeline.__class__.__name__}")
