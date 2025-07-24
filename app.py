# app.py

import os
import io
import streamlit as st
import pandas as pd
from nlp_pipeline import predict
from query_planner import load_data, handle_query

st.set_page_config(page_title="QSR CEO Performance Bot", layout="wide")
st.title("🍽️ QSR CEO Performance Bot")

DATA_PATH = "sales_data.csv"

# Load data from repo if present
df = None
if os.path.exists(DATA_PATH):
    try:
        df_raw = pd.read_csv(DATA_PATH)
        df = load_data(df_raw)
        st.success(f"✅ Loaded data from `{DATA_PATH}`")
    except Exception as e:
        st.error(f"❌ Failed to load `{DATA_PATH}`: {e}")

# Otherwise show uploader
if df is None:
    uploaded = st.file_uploader("Upload your `sales_data.csv`", type=["csv"])
    if uploaded:
        try:
            df_raw = pd.read_csv(uploaded)
            df = load_data(df_raw)
            st.success("✅ Data loaded successfully via upload!")
        except Exception as e:
            st.error(f"❌ Failed to load uploaded CSV: {e}")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []  # each item: {"role": "user"/"assistant", "content": str, ...}

# Chat interface
if df is not None:
    user_input = st.chat_input("Ask a performance question…")
    if user_input:
        # Record user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Compute answer
        intent, slots = predict(user_input)
        answer = handle_query(intent, slots, df)

        # Record assistant message (keep intent & slots for charting)
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "intent": intent,
            "slots": slots
        })

    # Render the full conversation
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])
            # If this was a TREND query, show chart immediately after
            if msg.get("intent") == "TREND":
                store = msg["slots"].get("STORE")
                metric = msg["slots"].get("METRIC")
                if store and metric:
                    chart_df = (
                        df[df["Store"] == store]
                        .set_index("Month")[metric]
                    )
                    st.line_chart(chart_df)

    # Download button for the entire conversation
    if st.session_state.messages:
        buffer = io.StringIO()
        for msg in st.session_state.messages:
            role = "YOU" if msg["role"] == "user" else "BOT"
            buffer.write(f"{role}: {msg['content']}\n\n")
        st.download_button(
            label="📥 Download Conversation",
            data=buffer.getvalue(),
            file_name="qsr_ceo_chat.txt",
            mime="text/plain"
        )
else:
    st.info("🔍 Please upload or commit `sales_data.csv` to get started.")
