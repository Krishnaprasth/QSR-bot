import streamlit as st
import pandas as pd
import sqlite3
from langchain.agents import create_pandas_dataframe_agent
from langchain.chat_models import ChatOpenAI

st.set_page_config(page_title="Data-Chat Bot")
st.title("🗄️ QSR CEO Data‑Chat Bot")

@st.cache_data
def load_data():
    conn = sqlite3.connect("sales_data.db")
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    return df

df = load_data()

if "agent" not in st.session_state:
    st.session_state.agent = create_pandas_dataframe_agent(
        ChatOpenAI(temperature=0.0, model_name="gpt-4"),
        df,
        verbose=False
    )

if "history" not in st.session_state:
    st.session_state.history = []

question = st.text_input("Ask a question about your store data:")
if st.button("Send") and question:
    st.session_state.history.append(("You", question))
    answer = st.session_state.agent.run(question)
    st.session_state.history.append(("GPT", answer))

for who, msg in st.session_state.history:
    if who == "You":
        st.markdown(f"**You:** {msg}")
    else:
        st.markdown(f"**GPT:** {msg}")