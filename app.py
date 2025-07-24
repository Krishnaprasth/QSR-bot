import os
import json
import sqlite3
import streamlit as st
import pandas as pd
import openai

# 0) Configuration
openai.api_key = os.getenv("OPENAI_API_KEY")
st.set_page_config(page_title="QSR CEO Data‑Chat Bot", layout="wide")

# 1) Load Data
@st.cache_data
def load_data():
    conn = sqlite3.connect("sales_data.db")
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    return df

df = load_data()

# 2) Session State
st.session_state.setdefault("questions", [])
st.session_state.setdefault("chat_history", [])

# 3) Sidebar
with st.sidebar:
    st.header("📜 Past Questions")
    if st.session_state.questions:
        for q in st.session_state.questions:
            st.markdown(f"- {q}")
    else:
        st.markdown("_No questions yet_")
    st.markdown("---")
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Full Data as CSV", csv_bytes, "sales_data.csv", "text/csv")
    st.markdown("---")
    if st.button("🗑️ Clear History"):
        st.session_state.questions.clear()
        st.session_state.chat_history.clear()
        st.experimental_rerun()

# 4) Main Chat
st.title("🗄️ QSR CEO Data‑Chat Bot")
question = st.text_input("Ask a question about your store data:")
if st.button("Send") and question:
    st.session_state.questions.append(question)
    st.session_state.chat_history.append({"user": question, "bot": None})

    # **Enhanced system prompt**:
    messages = [
        {"role": "system", "content": """
You are a QSR data expert. The pandas DataFrame `df` has columns:
  • Month (YYYY-MMM)  
  • Store (e.g. IND, KOR)  
  • Metric (e.g. Net Sales, COGS, etc.)  
  • Amount (numeric)

**Important rules**:
1. Treat “revenue” or “sales” or “net revenue” **all** as `Metric == "Net Sales"`.  
2. Normalize user periods like “Nov 24” → `"2024-Nov"`, “Dec 25” → `"2025-Dec"`.  
3. When asked “max revenue in XXX”, always:
   ```python
   temp = df[df["Metric"] == "Net Sales"]
   subset = temp[temp["Month"] == "<YYYY-MMM>"]
   store = subset.loc[subset["Amount"].idxmax(), "Store"]
   result = store
