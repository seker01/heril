from fastapi import FastAPI
from app.engines.analysis_engine import should_trigger_alert

app = FastAPI(title="BIST AI Intelligence")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/alerts/evaluate")
def evaluate_alert(payload: dict):
    return {"trigger": should_trigger_alert(payload)}
