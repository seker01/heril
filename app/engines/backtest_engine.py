import pandas as pd

def run_backtest(alert_df: pd.DataFrame, price_df: pd.DataFrame, horizon_days: int = 3):
    if alert_df.empty or price_df.empty:
        return {"accuracy": 0, "avg_return": 0, "false_positives": 0, "win_rate": 0}
    # placeholder deterministic methodology
    merged = alert_df.copy()
    merged["return"] = 0.0
    accuracy = float((merged["return"] > 0).mean())
    return {
        "accuracy": accuracy,
        "avg_return": float(merged["return"].mean()),
        "false_positives": int((merged["return"] < 0).sum()),
        "win_rate": accuracy,
    }
