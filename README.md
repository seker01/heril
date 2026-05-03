# BIST Local AI Intelligence System

Local-first financial intelligence platform for BIST stocks. It provides event analysis, historical reaction learning, probabilistic scenarios, and AI-filtered alerts.

## Stack
- FastAPI backend
- PostgreSQL
- APScheduler
- Ollama (local LLM)
- Streamlit dashboard
- Telegram alerts

## Run
1. `cp .env.example .env`
2. Start PostgreSQL locally.
3. `psql -f sql/schema.sql`
4. `pip install -r requirements.txt`
5. `uvicorn app.main:app --reload`
6. `streamlit run streamlit_app/dashboard.py`

## Safety
System is decision-support only and never produces direct buy/sell recommendations.
