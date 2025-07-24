import os, json, sqlite3
import streamlit as st
import pandas as pd
import openai

# 0) Config
openai.api_key = os.getenv("OPENAI_API_KEY")
st.set_page_config(page_title="QSR CEO Data‑Chat Bot", layout="wide")

# 1) Load data
@st.cache_data
def load_data():
    conn = sqlite3.connect("sales_data.db")
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    return df

df = load_data()

# 2) Init session state
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
    # Download full CSV
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Full Data as CSV", csv_bytes, "sales_data.csv", "text/csv")

    st.markdown("---")
    # Clear history button
    if st.button("🗑️ Clear History"):
        st.session_state.questions.clear()
        st.session_state.chat_history.clear()
        st.experimental_rerun()

# 4) Main chat interface
st.title("🗄️ QSR CEO Data‑Chat Bot")
question = st.text_input("Ask a question about your store data:")
if st.button("Send") and question:
    st.session_state.questions.append(question)
    st.session_state.chat_history.append({"user": question, "bot": None})

    messages = [
        {"role": "system", "content": """
You are a QSR data expert. The DataFrame `df` has columns:
  • Month (YYYY-MMM)  
  • Store (e.g. IND, KOR)  
  • Metric (e.g. Net Sales, COGS …)  
  • Amount (numeric)  

When asked for “sales”, filter for Metric=="Net Sales".  
For SSG in a single FY, build prior/current windows, sum, then compute growth.  
Assign final answer to variable `result`.
""".strip()},
        {"role": "user", "content": question}
    ]

    resp = openai.chat.completions.create(
        model="gpt-4-0613",
        messages=messages,
        functions=[{
            "name": "run_query",
            "description": "Execute pandas code on df and return result",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "pandas code that sets `result`"}
                },
                "required": ["code"]
            }
        }],
        function_call={"name": "run_query"},
    )

    choice = resp.choices[0].message
    fc = getattr(choice, "function_call", None)
    if fc:
        args = json.loads(fc.arguments)
        code = args.get("code", "")
        local = {"df": df}
        try:
            exec(code, {}, local)
            bot_result = local.get("result", None)
        except Exception as e:
            bot_result = f"❌ Error running code: {e}"
    else:
        bot_result = choice.content or ""

    st.session_state.chat_history[-1]["bot"] = bot_result

# 5) Render chat history
for turn in st.session_state.chat_history:
    st.markdown(f"**You:** {turn['user']}")
    st.markdown("**GPT:**")
    res = turn["bot"]
    if isinstance(res, pd.DataFrame):
        st.dataframe(res, use_container_width=True)
    elif isinstance(res, pd.Series):
        st.line_chart(res)
    elif isinstance(res, list) and all(isinstance(x, dict) for x in res):
        st.dataframe(pd.DataFrame(res), use_container_width=True)
    else:
        try:
            j = json.loads(res)
            if isinstance(j, list):
                st.dataframe(pd.DataFrame(j), use_container_width=True)
                continue
        except:
            pass
        st.markdown(res)
