import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from openai import OpenAI
from kpi import generate_report, generate_vintage_report, split_online_offline
from utils import load_data
from intent_manager import IntentManager

# Load data
df = load_data()

# Initialize OpenAI and Intent Manager
openai = OpenAI()
intent_mgr = IntentManager(openai)

# Function-calling schemas
functions = [
    {
        "name": "generate_report",
        "description": "Full performance report for a store and FY",
        "parameters": {
            "type": "object",
            "properties": {"store": {"type": "string"}, "fy": {"type": "string"}},
            "required": ["store", "fy"]
        }
    },
    {
        "name": "generate_vintage_report",
        "description": "Vintage segment KPI comparison",
        "parameters": {
            "type": "object",
            "properties": {"fy": {"type": "string"}},
            "required": ["fy"]
        }
    },
    {
        "name": "split_online_offline",
        "description": "Infer online vs offline split by stripping 5% GST",
        "parameters": {
            "type": "object",
            "properties": {"net_sales": {"type": "number"}, "gst_amount": {"type": "number"}},
            "required": ["net_sales", "gst_amount"]
        }
    }
]

st.title("QSR CEO Bot")

if "history" not in st.session_state:
    st.session_state.history = []

query = st.text_input("Ask me about your QSR data")
if st.button("Send") and query:
    top_intents = intent_mgr.get_top_intents(query)
    planning_hint = "I want you to perform: " + "; ".join(
        f"{i['name']} ({i['description']})" for i in top_intents
    )

    messages = [{"role": "system", "content": planning_hint}]
    for role, text in st.session_state.history:
        messages.append({"role": role, "content": text})
    messages.append({"role": "user", "content": query})

    resp = openai.chat.completions.create(
        model="gpt-4o", messages=messages, functions=functions, function_call="auto"
    )
    msg = resp.choices[0].message

    if getattr(msg, "function_call", None):
        name = msg.function_call.name
        args = msg.function_call.arguments
        if name == "generate_report":
            r = generate_report(df, **args)
            st.markdown("## Executive Summary"); st.write(r["executive_summary"])
            st.markdown("## KPI Table"); st.table(pd.DataFrame(r["kpi_table"]))
            st.markdown("## Cost Ratios"); st.table(pd.DataFrame(r["cost_ratio_table"]))
            st.markdown("## SSSG Detail"); st.json(r["sssg"])
            st.markdown("## Sales Trend")
            fig, ax = plt.subplots(); ax.plot(r["trend"]["months"], r["trend"]["values"], marker="o"); st.pyplot(fig)
            answer = f"Report for {args['store']} in {args['fy']} generated."
        elif name == "generate_vintage_report":
            rows = generate_vintage_report(df, **args)
            df_v = pd.DataFrame(rows)
            st.markdown(f"## Vintage Report — {args['fy']}"); st.table(df_v)
            buf = io.BytesIO()
            from matplotlib.backends.backend_pdf import PdfPages
            with PdfPages(buf) as pdf:
                fig, ax = plt.subplots(figsize=(8,3)); ax.axis("off")
                tbl = ax.table(cellText=df_v.values, colLabels=df_v.columns, loc="center")
                pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)
            st.download_button("Download Vintage Report", buf.getvalue(), file_name=f"vintage_{args['fy']}.pdf")
            answer = f"Vintage report for {args['fy']} generated."
        elif name == "split_online_offline":
            res = split_online_offline(**args)
            st.json(res)
            answer = f"Offline: ₹{res['offline_sales']} Lakhs, Online: ₹{res['online_sales']} Lakhs."
        else:
            answer = "Unknown function."
    else:
        answer = msg.content

    st.session_state.history.append(("assistant", answer))
    st.session_state.history.append(("user", query))

for role, text in st.session_state.history:
    st.markdown(f"**{role.title()}:** {text}")