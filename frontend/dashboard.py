"""Streamlit frontend dashboard for local stock analysis terminal."""
from __future__ import annotations

import os

import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Local Stock Analysis", layout="wide")
st.title("📈 Local Stock Analysis Terminal")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Live Stock Search")
    ticker = st.text_input("Ticker", "ASELS")
    st.caption(f"Selected ticker: {ticker}")

with col2:
    st.subheader("Evaluation Trigger")
    as_of = st.date_input("Evaluate due predictions as of")
    if st.button("Run Evaluation"):
        resp = requests.post(f"{API_URL}/evaluate", params={"as_of": as_of.isoformat()}, timeout=30)
        st.success(resp.json())

st.subheader("Accuracy Statistics")
try:
    data = requests.get(f"{API_URL}/metrics/accuracy", timeout=30).json()
    acc_df = pd.DataFrame(data)
except Exception:
    acc_df = pd.DataFrame(columns=["ticker", "horizon", "n", "accuracy", "mean_error"])

st.dataframe(acc_df, width="stretch")

left, right = st.columns(2)
with left:
    st.subheader("Model Confidence Heatmap")
    if not acc_df.empty and {"ticker", "horizon", "accuracy"}.issubset(acc_df.columns):
        pivot = acc_df.pivot(index="ticker", columns="horizon", values="accuracy").fillna(0)
        st.dataframe(pivot.style.background_gradient(cmap="RdYlGn"), width="stretch")

    st.subheader("Feature Importance Visual")
    sample_importance = pd.DataFrame(
        {
            "feature": ["momentum", "technical", "volatility", "macro", "sentiment"],
            "importance": [0.24, 0.20, 0.18, 0.16, 0.22],
        }
    )
    st.bar_chart(sample_importance.set_index("feature"))

with right:
    st.subheader("Error Analysis Dashboard")
    if not acc_df.empty and "mean_error" in acc_df.columns:
        st.line_chart(acc_df.set_index("ticker")["mean_error"])

    st.subheader("LLM Reasoning Panel")
    st.info("Displays root-cause JSON from local Ollama engine (query DB in production wiring).")

    st.subheader("Model Weight Evolution")
    weight_hist = pd.DataFrame(
        {
            "step": [1, 2, 3, 4],
            "momentum": [0.2, 0.25, 0.23, 0.22],
            "technical": [0.2, 0.19, 0.20, 0.21],
            "sentiment": [0.2, 0.22, 0.24, 0.25],
        }
    ).set_index("step")
    st.line_chart(weight_hist)
