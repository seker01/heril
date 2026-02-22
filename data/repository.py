"""Repository layer for local stock analysis system."""
from __future__ import annotations

from datetime import date
from typing import Any

import json

import pandas as pd
from sqlalchemy import text

from db.connection import get_engine


class LocalRepository:
    """Database operations for predictions/evaluation/sentiment/weights."""

    def __init__(self) -> None:
        self.engine = get_engine()

    def insert_prediction(self, payload: dict[str, Any]) -> int:
        sql = text(
            """
            INSERT INTO predictions (
                ticker,prediction_date,horizon,predicted_return,predicted_direction,
                feature_snapshot,model_version,confidence
            ) VALUES (
                :ticker,:prediction_date,:horizon,:predicted_return,:predicted_direction,
                CAST(:feature_snapshot AS JSONB),:model_version,:confidence
            ) RETURNING id
            """
        )
        with self.engine.begin() as conn:
            row = conn.execute(sql, {**payload, "feature_snapshot": json.dumps(payload["feature_snapshot"])}).fetchone()
        return int(row[0])

    def predictions_due(self, as_of: date) -> pd.DataFrame:
        sql = text(
            """
            SELECT p.*
            FROM predictions p
            LEFT JOIN prediction_results r ON r.prediction_id = p.id
            WHERE r.prediction_id IS NULL
              AND p.prediction_date + CASE
                    WHEN p.horizon = '7d' THEN INTERVAL '7 day'
                    WHEN p.horizon = '30d' THEN INTERVAL '30 day'
                    ELSE INTERVAL '90 day'
                  END <= :as_of
            """
        )
        return pd.read_sql_query(sql, self.engine, params={"as_of": as_of})

    def get_prices(self, ticker: str, start_date: date, end_date: date) -> pd.DataFrame:
        sql = text(
            """
            SELECT date, close, market_regime, macro_snapshot
            FROM price_history
            WHERE ticker = :ticker AND date BETWEEN :start_date AND :end_date
            ORDER BY date
            """
        )
        return pd.read_sql_query(sql, self.engine, params={"ticker": ticker, "start_date": start_date, "end_date": end_date})

    def save_prediction_result(self, row: dict[str, Any]) -> None:
        sql = text(
            """
            INSERT INTO prediction_results (prediction_id, actual_return, accuracy, is_correct, error_magnitude)
            VALUES (:prediction_id,:actual_return,:accuracy,:is_correct,:error_magnitude)
            ON CONFLICT (prediction_id) DO UPDATE
            SET actual_return = EXCLUDED.actual_return,
                accuracy = EXCLUDED.accuracy,
                is_correct = EXCLUDED.is_correct,
                error_magnitude = EXCLUDED.error_magnitude,
                evaluated_at = NOW()
            """
        )
        with self.engine.begin() as conn:
            conn.execute(sql, row)

    def latest_sentiment(self, ticker: str, on_date: date) -> dict[str, float]:
        sql = text(
            """
            SELECT news_polarity,social_sentiment,volume_spike,geopolitical_signal,composite_score
            FROM sentiment_scores
            WHERE ticker=:ticker AND score_date <= :on_date
            ORDER BY score_date DESC
            LIMIT 1
            """
        )
        with self.engine.begin() as conn:
            r = conn.execute(sql, {"ticker": ticker, "on_date": on_date}).mappings().fetchone()
        return dict(r) if r else {}

    def save_root_cause(self, prediction_id: int, payload: dict[str, Any], llm_model: str) -> None:
        sql = text(
            """
            INSERT INTO root_cause_analysis (
                prediction_id,main_failure_reason,missed_driver,weak_signal,
                overweighted_signal,suggested_weight_adjustments,confidence,llm_model
            ) VALUES (
                :prediction_id,:main_failure_reason,:missed_driver,:weak_signal,
                :overweighted_signal,CAST(:suggested_weight_adjustments AS JSONB),:confidence,:llm_model
            )
            ON CONFLICT (prediction_id) DO UPDATE
            SET main_failure_reason = EXCLUDED.main_failure_reason,
                missed_driver = EXCLUDED.missed_driver,
                weak_signal = EXCLUDED.weak_signal,
                overweighted_signal = EXCLUDED.overweighted_signal,
                suggested_weight_adjustments = EXCLUDED.suggested_weight_adjustments,
                confidence = EXCLUDED.confidence,
                llm_model = EXCLUDED.llm_model
            """
        )
        payload = {**payload, "prediction_id": prediction_id, "llm_model": llm_model, "suggested_weight_adjustments": json.dumps(payload.get("suggested_weight_adjustments", {}))}
        with self.engine.begin() as conn:
            conn.execute(sql, payload)

    def get_latest_weights(self, ticker: str, regime: str, model_version: str) -> dict[str, float]:
        sql = text("""SELECT weights FROM model_weights WHERE ticker=:ticker AND regime=:regime AND model_version=:model_version ORDER BY updated_at DESC LIMIT 1""")
        with self.engine.begin() as conn:
            row = conn.execute(sql, {"ticker": ticker, "regime": regime, "model_version": model_version}).fetchone()
        return dict(row[0]) if row else {}

    def upsert_weights(self, ticker: str, regime: str, model_version: str, weights: dict[str, float], reinforcement_score: float) -> None:
        sql = text(
            """
            INSERT INTO model_weights (ticker, regime, model_version, weights, reinforcement_score)
            VALUES (:ticker,:regime,:model_version,CAST(:weights AS JSONB),:reinforcement_score)
            ON CONFLICT (ticker, regime, model_version) DO UPDATE
            SET weights = EXCLUDED.weights,
                reinforcement_score = EXCLUDED.reinforcement_score,
                updated_at = NOW()
            """
        )
        with self.engine.begin() as conn:
            conn.execute(sql, {
                "ticker": ticker,
                "regime": regime,
                "model_version": model_version,
                "weights": json.dumps(weights),
                "reinforcement_score": reinforcement_score,
            })

    def accuracy_summary(self) -> pd.DataFrame:
        sql = text(
            """
            SELECT p.ticker, p.horizon, COUNT(*) as n,
                   AVG(CASE WHEN r.is_correct THEN 1 ELSE 0 END) AS accuracy,
                   AVG(r.error_magnitude) AS mean_error
            FROM predictions p
            JOIN prediction_results r ON p.id = r.prediction_id
            GROUP BY p.ticker, p.horizon
            ORDER BY n DESC
            """
        )
        return pd.read_sql_query(sql, self.engine)
