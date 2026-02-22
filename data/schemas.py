"""Pydantic schemas for API and services."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


Horizon = Literal["7d", "30d", "90d"]
Direction = Literal["UP", "DOWN", "FLAT"]


class PredictionCreate(BaseModel):
    ticker: str
    prediction_date: date
    horizon: Horizon
    predicted_return: float
    predicted_direction: Direction
    feature_snapshot: dict[str, Any]
    model_version: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class PredictionResultView(BaseModel):
    prediction_id: int
    actual_return: float
    accuracy: float
    is_correct: bool
    error_magnitude: float
    evaluated_at: datetime


class RootCausePayload(BaseModel):
    main_failure_reason: str
    missed_driver: str
    weak_signal: str
    overweighted_signal: str
    suggested_weight_adjustments: dict[str, float]
    confidence: float
