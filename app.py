
import streamlit as st
import pandas as pd
from query_router import route_query

st.set_page_config(page_title="QSR CEO Bot", layout="wide")
st.title("QSR CEO Performance Bot")

@st.cache_data
def load_data():
    return pd.read_csv("QSR_CEO_CLEANED_FY22_TO_FY26_FULL_FINAL.csv")

df = load_data()

query = st.text_input("Ask a performance question:")

if query:
    response = route_query(query, df)
    if response is not None:
        st.success("Answered via logic engine")
        st.dataframe(response)
    else:
        st.warning("Query not recognized. Please rephrase or refine.")
