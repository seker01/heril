1. Load schema: `psql -f sql/schema.sql`
2. Start backend: `uvicorn app.main:app --reload`
3. Hit `/health`
4. Trigger alert evaluation with sample LLM output JSON
5. Run Streamlit UI
6. Execute scheduler and verify jobs fire
7. Run backtest module with historical tables to write `prediction_results`
