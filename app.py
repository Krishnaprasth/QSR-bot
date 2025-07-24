import os
import json
import streamlit as st
import pandas as pd
import sqlite3
import openai

# 1) Configure your OpenAI key in the environment
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="QSR CEO Data‑Chat Bot")
st.title("🗄️ QSR CEO Data‑Chat Bot")

# 2) Load your sales_data.db into a pandas DataFrame (cached)
@st.cache_data
def load_data():
    conn = sqlite3.connect("sales_data.db")
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    return df

df = load_data()

# 3) Conversation state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": """
You are a QSR data expert. The pandas DataFrame `df` has these columns:
  - `Month`: strings like "2024-Feb", "2023-Dec"
  - `Store`: store codes, e.g. "HSR", "KOR"
  - `Metric`: metric names, e.g. "Net Sales", "COGS (food +packaging)", etc.
  - `Amount`: numeric value of that metric for that store/month.

When asked for "sales", filter **Metric == 'Net Sales'** and always use `df['Month']` (not `df['Date']`).
Dates like "dec 24" or "Dec-2024" should map to `"2024-Dec"`.  
Return your answer by assigning the final output to a variable named `result`.
""".strip()}
    ]
if "history" not in st.session_state:
    st.session_state.history = []

# 4) User input
question = st.text_input("Ask a question about your store data:")
if st.button("Send") and question:
    # Append user question
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.history.append(("You", question))

    # Call ChatGPT with function schema (v1 API)
    response = openai.chat.completions.create(
        model="gpt-4-0613",
        messages=st.session_state.messages,
        functions=[
            {
                "name": "run_query",
                "description": "Execute pandas code on the DataFrame `df` and return the result in `result`",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "pandas code that sets a variable `result`."}
                    },
                    "required": ["code"]
                },
            }
        ],
        function_call={"name": "run_query"},
    )

    choice = response.choices[0]
    message = choice.message
    func_call = getattr(message, "function_call", None)

    if func_call:
        # Parse the JSON arguments to get the code
        args = json.loads(func_call.arguments)
        code = args.get("code", "")
        local_vars = {"df": df}
        try:
            exec(code, {}, local_vars)
            result = local_vars.get("result", "✅ Ran code but no `result` returned.")
        except Exception as e:
            result = f"❌ Error running code: {e}"
        # Add the function response back into the chat context
        st.session_state.messages.append({
            "role": "function",
            "name": "run_query",
            "content": str(result)
        })
        st.session_state.history.append(("GPT", result))
    else:
        # No function call? Just a plain assistant reply
        answer = message.content or ""
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.history.append(("GPT", answer))

# 5) Render chat history
for who, text in st.session_state.history:
    if who == "You":
        st.markdown(f"**You:** {text}")
    else:
        st.markdown(f"**GPT:** {text}")
