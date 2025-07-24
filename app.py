import os
import streamlit as st
import pandas as pd
from nlp_pipeline import predict
from query_planner import load_data, handle_query

st.set_page_config(page_title="QSR CEO Performance Bot")
st.title("QSR CEO Performance Bot")

# Load data (uploaded or local)
uploaded = st.file_uploader("Upload your sales_data.csv (optional)", type=["csv"])
if uploaded is not None:
    df_raw = pd.read_csv(uploaded)
elif os.path.exists("sales_data.csv"):
    st.info("🔍 Using local sales_data.csv from repo")
    df_raw = pd.read_csv("sales_data.csv")
else:
    st.warning("📂 No CSV found—please upload sales_data.csv or add it to the repo root.")
    st.stop()

# Prepare DataFrame
try:
    df = load_data(df_raw)
    st.success("✅ Data loaded successfully!")
except Exception as e:
    st.error(f"Failed to prepare data: {e}")
    st.stop()

# Container to hold all Q&As
chat_container = st.container()

# Use a form to clear input on each submit
with st.form("query_form", clear_on_submit=True):
    user_question = st.text_input("Ask a performance question:")
    submitted = st.form_submit_button("Ask")

if submitted and user_question:
    intent, slots = predict(user_question)
    answer = handle_query(intent, slots, df)
    # Append this Q&A to the container
    with chat_container:
        st.markdown(f"**Q:** {user_question}")
        st.markdown(f"**A:** {answer}")
        # If it was a TREND query, show the chart too
        if intent == "TREND" and slots.get("STORE") and slots.get("METRIC"):
            series = df[df["Store"] == slots["STORE"]].set_index("Month")[slots["METRIC"]]
            st.line_chart(series)
