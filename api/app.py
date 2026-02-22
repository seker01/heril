"""FastAPI backend for fully local stock analysis terminal system."""
from __future__ import annotations

from datetime import date

from fastapi import FastAPI

from data.repository import LocalRepository
from data.schemas import PredictionCreate
from evaluation.prediction_evaluator import PredictionEvaluator
from evaluation.root_cause_engine import RootCauseEngine
from llm.ollama_client import OllamaClient
from training.weight_updater import ReinforcementWeightUpdater

app = FastAPI(title="Local Stock Analysis Terminal", version="1.0.0")
repo = LocalRepository()
evaluator = PredictionEvaluator(
    repository=repo,
    root_cause_engine=RootCauseEngine(llm_client=OllamaClient.from_env()),
    weight_updater=ReinforcementWeightUpdater(),
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "local-only"}


@app.post("/predictions")
def create_prediction(payload: PredictionCreate) -> dict[str, int]:
    prediction_id = repo.insert_prediction(payload.model_dump())
    return {"prediction_id": prediction_id}


@app.post("/evaluate")
def evaluate(as_of: date) -> dict[str, int]:
    evaluated = evaluator.run(as_of)
    return {"evaluated": evaluated}


@app.get("/metrics/accuracy")
def accuracy_metrics() -> list[dict[str, object]]:
    return repo.accuracy_summary().to_dict(orient="records")
