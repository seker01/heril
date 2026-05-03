import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="BIST Intelligence", layout="wide")
st.title("BIST AI Stock Intelligence Dashboard")

stock = st.selectbox("Stock selector", ["ASELS.IS", "THYAO.IS", "BIMAS.IS"])
st.subheader("Watchlist")
st.write([stock])

st.subheader("Price charts")
df = pd.DataFrame({"date": pd.date_range("2026-01-01", periods=30), "close": range(30)})
st.plotly_chart(px.line(df, x="date", y="close"), use_container_width=True)

st.subheader("Recent news")
st.info("RSS-backed latest news list")

st.subheader("AI analysis panel")
st.json({"confidence_score": 78, "risk_level": "medium", "alternative_scenarios": ["neutral drift", "macro shock"]})

st.subheader("Historical reaction insights")
st.write("Pattern learning summary per stock.")

st.subheader("Scenario panel")
st.write("Positive/negative probabilistic scenarios.")

st.subheader("Alert history")
st.table(pd.DataFrame([{"stock": stock, "impact": "positive", "confidence": 78}]))

st.subheader("Risk score")
st.metric("Risk level", "Medium")

st.subheader("Macro sensitivity")
st.write("USDTRY, policy-rate, CPI sensitivity.")

st.caption("Not investment advice.")
