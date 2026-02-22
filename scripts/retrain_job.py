"""Periodic retrain job for local system."""
from __future__ import annotations

import pandas as pd
from sqlalchemy import text

from db.connection import get_engine
from training.retrainer import PeriodicRetrainer


def run_retrain(model_version: str = "v1-local") -> None:
    engine = get_engine()
    query = text(
        """
        SELECT p.ticker, p.model_version, p.feature_snapshot, r.actual_return
        FROM predictions p
        JOIN prediction_results r ON r.prediction_id = p.id
        WHERE p.model_version = :model_version
        """
    )
    df = pd.read_sql_query(query, engine, params={"model_version": model_version})
    if df.empty:
        print("No data available for retraining")
        return

    features = pd.json_normalize(df["feature_snapshot"])
    train_df = pd.concat([features, df[["ticker", "actual_return"]]], axis=1)
    feature_cols = [c for c in features.columns if pd.api.types.is_numeric_dtype(features[c])]

    retrainer = PeriodicRetrainer(min_rows=10)
    new_weights = retrainer.retrain_weights(train_df, feature_cols=feature_cols, target_col="actual_return")
    print("New weights", new_weights)


if __name__ == "__main__":
    run_retrain()
