"""Evaluate due predictions and trigger root-cause/remediation loop."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

import numpy as np
import pandas as pd

from data.repository import LocalRepository
from evaluation.root_cause_engine import RootCauseEngine
from training.weight_updater import ReinforcementWeightUpdater


HORIZON_TO_DAYS = {"7d": 7, "30d": 30, "90d": 90}


@dataclass(slots=True)
class PredictionEvaluator:
    """Evaluate predictions and route incorrect cases into learning loop."""

    repository: LocalRepository
    root_cause_engine: RootCauseEngine
    weight_updater: ReinforcementWeightUpdater

    def run(self, as_of: date) -> int:
        """Evaluate all due predictions; return count evaluated."""
        due = self.repository.predictions_due(as_of)
        processed = 0
        for row in due.itertuples(index=False):
            result = self._evaluate_row(row)
            self.repository.save_prediction_result(result)
            if not result["is_correct"]:
                self._process_failure(row, result)
            processed += 1
        return processed

    def _evaluate_row(self, row: Any) -> dict[str, Any]:
        start_date = row.prediction_date
        end_date = start_date + timedelta(days=HORIZON_TO_DAYS[row.horizon])
        prices = self.repository.get_prices(row.ticker, start_date, end_date)
        if prices.empty or prices.shape[0] < 2:
            actual_return = np.nan
        else:
            actual_return = float(prices["close"].iloc[-1] / prices["close"].iloc[0] - 1)

        pred_sign = np.sign(row.predicted_return)
        real_sign = np.sign(actual_return) if not np.isnan(actual_return) else 0
        is_correct = bool(pred_sign == real_sign and not np.isnan(actual_return))
        accuracy = 1.0 if is_correct else 0.0
        error_magnitude = float(abs(row.predicted_return - actual_return)) if not np.isnan(actual_return) else 1.0
        return {
            "prediction_id": int(row.id),
            "actual_return": float(actual_return if not np.isnan(actual_return) else 0.0),
            "accuracy": accuracy,
            "is_correct": is_correct,
            "error_magnitude": error_magnitude,
        }

    def _process_failure(self, row: Any, eval_result: dict[str, Any]) -> None:
        price_ctx = self.repository.get_prices(row.ticker, row.prediction_date, row.prediction_date + timedelta(days=HORIZON_TO_DAYS[row.horizon]))
        sentiment = self.repository.latest_sentiment(row.ticker, row.prediction_date)
        market_condition = price_ctx["market_regime"].dropna().iloc[-1] if "market_regime" in price_ctx and not price_ctx.empty else "unknown"
        macro = price_ctx["macro_snapshot"].dropna().iloc[-1] if "macro_snapshot" in price_ctx and not price_ctx.empty else {}

        context = {
            "ticker": row.ticker,
            "feature_snapshot": row.feature_snapshot,
            "sentiment_score": sentiment,
            "macro_data": macro,
            "market_condition": market_condition,
            "actual_outcome": eval_result,
        }
        rca = self.root_cause_engine.analyze(context)
        self.repository.save_root_cause(int(row.id), rca, self.root_cause_engine.llm_client.model)

        old_w = self.repository.get_latest_weights(row.ticker, str(market_condition), row.model_version)
        new_w = self.weight_updater.apply(old_w or {k: 0.2 for k in ["momentum", "technical", "volatility", "macro", "sentiment"]}, rca["suggested_weight_adjustments"])
        self.repository.upsert_weights(row.ticker, str(market_condition), row.model_version, new_w, reinforcement_score=1 - eval_result["accuracy"])
