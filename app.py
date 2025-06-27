import streamlit as st
import pandas as pd
from logic.metrics_engine import compute_metric
from logic.cohort_logic import analyze_store_cohort
from logic.counterfactuals import run_counterfactual_analysis
from logic.semantic_router import semantic_router
from utils.helpers import extract_available_months

st.set_page_config(page_title="QSR CEO Bot", layout="wide")
st.title("QSR CEO Bot")

@st.cache_data
def load_data():
    return pd.read_csv("final_cleaned_50_months.csv")

# Load the pre-cleaned dataset
df = load_data()

# Show history of queries and answers in sidebar
if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.subheader("Query History")
    for i, (q, a) in enumerate(st.session_state.history):
        st.markdown(f"**Q{i+1}:** {q}")
        st.markdown(f"{a}")
    if st.button("Clear History"):
        st.session_state.history = []

# Main chat interface
query = st.text_input("Ask your question about store performance:")

if query:
    try:
        response = semantic_router(query, df)
    except Exception as e:
        response = f"❌ Error: {str(e)}"

    st.write(response)
    st.session_state.history.append((query, response))
