"""End-to-end orchestration of feature, alpha, and reporting steps."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from analysis.factor_analyzer import FactorAnalyzer
from backtest.outcome_tracker import OutcomeTracker
from core.alpha_engine import HybridAlpha
from core.feature_engine import FeatureEngine, build_rebalance_dates
from core.regime_detector import RegimeDetector
from db.repository import SQLRepository


@dataclass(slots=True)
class ResearchPipeline:
    """High-level workflow for research/backtest runs."""

    repository: SQLRepository
    feature_engine: FeatureEngine
    regime_detector: RegimeDetector
    alpha_engine: HybridAlpha
    outcome_tracker: OutcomeTracker
    factor_analyzer: FactorAnalyzer

    def run_feature_build(self, tickers: list[str], macro_df: pd.DataFrame, sentiment_df: pd.DataFrame) -> pd.DataFrame:
        prices = self.feature_engine.load_prices(tickers)
        rebal = build_rebalance_dates(prices)
        feats = self.feature_engine.compute_features(prices, macro_df, sentiment_df, rebal)
        self.feature_engine.save_features(feats)
        return feats
