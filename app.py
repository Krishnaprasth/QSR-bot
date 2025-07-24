import streamlit as st
import pandas as pd
from nlp_pipeline import predict
from query_planner import load_data, handle_query

st.set_page_config(page_title="QSR CEO Performance Bot")
st.title("QSR CEO Performance Bot")

data_file = st.file_uploader("Upload your sales_data.csv", type=["csv"])
if data_file:
    df_raw = pd.read_csv(data_file)
    df = load_data(data_file)
    st.success("Data loaded successfully!")
    question = st.text_input("Ask a performance question:")
    if question:
        intent, slots = predict(question)
        result = handle_query(intent, slots, df)
        st.write(result)
        if intent == "TREND" and "STORE" in slots and "METRIC" in slots:
            chart_data = df[df["Store"] == slots["STORE"]].set_index("Month")[slots["METRIC"]]
            st.line_chart(chart_data)
