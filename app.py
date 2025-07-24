import streamlit as st
import pandas as pd
import sqlite3

# ← direct import avoids langchain_community
from langchain.llms.openai import OpenAI
from langchain.agents import initialize_agent
from langchain.agents.agent_toolkits import PandasToolkit

st.set_page_config(page_title="QSR CEO Data‑Chat Bot")
st.title("🗄️ QSR CEO Data‑Chat Bot")

@st.cache_data
def load_data():
    conn = sqlite3.connect("sales_data.db")
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    return df

df = load_data()

if "agent" not in st.session_state:
    llm = OpenAI(temperature=0.0, model_name="gpt-4")
    toolkit = PandasToolkit(df=df, llm=llm)
    tools = toolkit.get_tools()
    agent = initialize_agent(
        tools,
        llm,
        agent="zero-shot-react-description",
        verbose=False
    )
    st.session_state.agent = agent

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
