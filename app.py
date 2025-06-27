
import streamlit as st
import pandas as pd
from logic.metrics_engine import compute_metric
from logic.cohort_logic import tag_cohorts
from logic.counterfactuals import simulate_scenario
from logic.semantic_router import route_query

st.set_page_config(layout="wide")
st.title("QSR CEO Bot")

uploaded_file = st.file_uploader("Upload Final Cleaned CSV", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df = tag_cohorts(df)
    query = st.text_input("Ask a financial question:")
    if query:
        result = route_query(query, df)
        st.write(result)
        st.download_button("Download Result", result.to_csv(index=False), "result.csv")
