import os
import json
import streamlit as st
import pandas as pd
import sqlite3
import openai

# Configure your OpenAI key
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="QSR CEO Data‑Chat Bot", layout="wide")
st.title("🗄️ QSR CEO Data‑Chat Bot")

# Load data once
@st.cache_data
def load_data():
    conn = sqlite3.connect("sales_data.db")
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    return df

df = load_data()

# --- Sidebar UI ---
with st.sidebar:
    st.header("📜 Past Questions")
    if "history" in st.session_state and st.session_state.history:
        for who, content in st.session_state.history:
            if who == "You":
                st.markdown(f"- {content}")
    else:
        st.markdown("_No questions yet_")
    st.markdown("---")
    st.download_button(
        label="⬇️ Download Full Data as CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="sales_data.csv",
        mime="text/csv"
    )

# Initialize conversation state
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system",
        "content": """
You are a QSR data expert. The pandas DataFrame `df` has columns:
  - Month (YYYY-MMM), Store, Metric, Amount
Return your answer by assigning the final output to `result`.  
If result is a DataFrame or Series, I'll render it as a table or chart.
""".strip()
    }]
if "history" not in st.session_state:
    st.session_state.history = []

# Main chat input
question = st.text_input("Ask a question about your store data:")
if st.button("Send") and question:
    st.session_state.messages.append({"role":"user","content":question})
    st.session_state.history.append(("You", question))

    # Call GPT‑4 with function‑calling
    response = openai.chat.completions.create(
        model="gpt-4-0613",
        messages=st.session_state.messages,
        functions=[{
            "name": "run_query",
            "description": "Execute pandas code on df and return result",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type":"string","description":"pandas code that defines `result`"}
                },
                "required":["code"]
            }
        }],
        function_call={"name":"run_query"}
    )

    choice = response.choices[0]
    msg = choice.message
    func_call = getattr(msg, "function_call", None)

    if func_call:
        args = json.loads(func_call.arguments)
        code = args.get("code","")
        local = {"df": df}
        try:
            exec(code, {}, local)
            result = local.get("result", None)
        except Exception as e:
            result = f"❌ Error running code: {e}"
        # Append the function result back
        st.session_state.messages.append({
            "role":"function",
            "name":"run_query",
            "content": str(result)
        })
        st.session_state.history.append(("GPT", result))
    else:
        # Plain assistant reply
        answer = msg.content or ""
        st.session_state.messages.append({"role":"assistant","content":answer})
        st.session_state.history.append(("GPT", answer))

# Render chat + rich outputs
for who, content in st.session_state.history:
    if who == "You":
        st.markdown(f"**You:** {content}")
    else:
        st.markdown(f"**GPT:**")
        # Rich rendering based on type
        if isinstance(content, pd.DataFrame):
            st.dataframe(content, use_container_width=True)
        elif isinstance(content, pd.Series):
            st.line_chart(content)
        elif isinstance(content, list) and all(isinstance(x, dict) for x in content):
            st.dataframe(pd.DataFrame(content), use_container_width=True)
        else:
            # Try JSON→DataFrame
            try:
                obj = json.loads(content)
                if isinstance(obj, list):
                    st.dataframe(pd.DataFrame(obj), use_container_width=True)
                    continue
            except:
                pass
            st.markdown(f"{content}")
