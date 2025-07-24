import os
import streamlit as st
import pandas as pd
from nlp_pipeline import predict
from query_planner import load_data, handle_query

st.set_page_config(page_title="QSR CEO Performance Bot")
st.title("QSR CEO Performance Bot")

# Load CSV (upload or local)
uploaded = st.file_uploader("Upload your sales_data.csv (optional)", type=["csv"])
if uploaded:
    df_raw = pd.read_csv(uploaded)
elif os.path.exists("sales_data.csv"):
    st.info("🔍 Using local sales_data.csv")
    df_raw = pd.read_csv("sales_data.csv")
else:
    st.warning("📂 No CSV found—please upload or add sales_data.csv in root.")
    st.stop()

# Prepare data
try:
    df = load_data(df_raw)
    st.success("✅ Data loaded!")
except Exception as e:
    st.error(f"Data prep failed: {e}")
    st.stop()

chat = st.container()
with st.form("qform", clear_on_submit=True):
    q = st.text_input("Ask a performance question:")
    go = st.form_submit_button("Ask")

if go and q:
    intent, slots = predict(q)
    slots["RAW_TEXT"] = q
    ans = handle_query(intent, slots, df)
    with chat:
        st.markdown(f"**Q:** {q}")
        st.markdown(f"**A:** {ans}")
        if intent == "TREND" and slots.get("STORE") and slots.get("METRIC"):
            series = df[df["Store"]==slots["STORE"]].set_index("Month")[slots["METRIC"]]
            st.line_chart(series)
