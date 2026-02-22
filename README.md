# Local Stock Analysis Terminal (PostgreSQL + FastAPI + Streamlit + Ollama)

A fully local system for stock prediction, evaluation, root-cause feedback, dynamic model weighting, and periodic retraining.

## Architecture

- **Backend**: FastAPI (`api/app.py`)
- **Frontend**: Streamlit (`frontend/dashboard.py`)
- **Database**: PostgreSQL (`db/migrations/002_local_terminal_schema.sql`)
- **Local LLM**: Ollama + Llama3/Qwen (`llm/ollama_client.py`)
- **Sentiment**: Local FinGPT-style sentiment scoring (`sentiment/fingpt_local.py`)

## Project Structure

- `data/` repository + API schemas
- `models/` predictor model
- `llm/` local Ollama client
- `sentiment/` FinGPT-style scorer
- `training/` weight updater + retrainer
- `evaluation/` evaluator, root-cause engine, defensive detector
- `frontend/` Streamlit dashboard
- `api/` FastAPI service
- `db/` connection and migrations
- `scripts/` operational jobs (retraining)
- `tests/` unit tests

## Required Tables

- `stocks`
- `price_history`
- `predictions`
- `prediction_results`
- `sentiment_scores`
- `model_weights`
- `root_cause_analysis`

## Run

```bash
pip install -r requirements.txt
cp .env.sample .env
```

Apply migration SQL from `db/migrations/002_local_terminal_schema.sql`.

Start backend:

```bash
uvicorn api.app:app --reload
```

Start frontend:

```bash
streamlit run frontend/dashboard.py
```

Run tests:

```bash
pytest -q
```

## Local-only policy

- No OpenAI API usage.
- Root cause analysis uses local Ollama endpoint.
- Sentiment module runs locally with deterministic fallback logic.

## Meta-learning capability

`evaluation/defensive_detector.py` flags assets as `defensive_or_independent` if they repeatedly outperform during market downturns.
