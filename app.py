import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from openai import OpenAI
from kpi import generate_report, generate_vintage_report, split_online_offline
from utils import load_data

# 1) Load data once
@st.experimental_singleton
def get_data():
    return load_data("data/sales_data.csv")
df = get_data()

# 2) Define function-calling schemas
functions = [
    {
        "name": "generate_report",
        "description": "Full performance report for a store and FY",
        "parameters": {
            "type": "object",
            "properties": {
                "store": {"type": "string"},
                "fy":    {"type": "string"}
            },
            "required": ["store","fy"]
        }
    },
    {
        "name": "generate_vintage_report",
        "description": "KPI comparison for New/Emerging/Established stores",
        "parameters": {
            "type": "object",
            "properties": {
                "fy": {"type":"string"}
            },
            "required": ["fy"]
        }
    },
    {
        "name": "split_online_offline",
        "description": "Infer offline vs online sales by stripping 5% GST",
        "parameters": {
            "type": "object",
            "properties": {
                "net_sales":  {"type":"number"},
                "gst_amount": {"type":"number"}
            },
            "required": ["net_sales","gst_amount"]
        }
    }
]

# 3) Initialize OpenAI client
openai = OpenAI()

# 4) Chat UI
st.title("QSR CEO Bot")

if "history" not in st.session_state:
    st.session_state.history = []

query = st.text_input("Ask me about your QSR data")
if st.button("Send") and query:
    messages = [{"role":"system","content":"You are a QSR financial analyst. Use the available functions when possible."}]
    messages += [{"role":r, "content":c} for r,c in st.session_state.history]
    messages += [{"role":"user","content":query}]

    resp = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        functions=functions,
        function_call="auto"
    )
    msg = resp.choices[0].message

    if msg.get("function_call"):
        name, args = msg.function_call.name, msg.function_call.arguments

        if name == "generate_report":
            report = generate_report(**args)
            st.markdown("## Executive Summary")
            st.write(report["executive_summary"])
            st.markdown("## KPI Table")
            st.table(pd.DataFrame(report["kpi_table"]))
            st.markdown("## Cost Ratios")
            st.table(pd.DataFrame(report["cost_ratio_table"]))
            st.markdown("## SSSG Detail")
            st.json(report["sssg"])
            st.markdown("## Sales Trend")
            fig, ax = plt.subplots()
            ax.plot(report["trend"]["months"], report["trend"]["values"], marker="o")
            st.pyplot(fig)
            answer = f"Generated full report for {args['store']} in {args['fy']}."

        elif name == "generate_vintage_report":
            rows = generate_vintage_report(**args)
            df_v = pd.DataFrame(rows)
            st.markdown(f"## Vintage Report — {args['fy']}")
            st.table(df_v)
            buf = io.BytesIO()
            with PdfPages(buf) as pdf:
                fig, ax = plt.subplots(figsize=(8,3))
                ax.axis("off")
                tbl = ax.table(cellText=df_v.values, colLabels=df_v.columns, loc="center")
                pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)
            st.download_button("Download Vintage Report (PDF)", buf.getvalue(), file_name=f"vintage_{args['fy']}.pdf")
            answer = f"Generated vintage report for {args['fy']}."

        elif name == "split_online_offline":
            res = split_online_offline(**args)
            st.json(res)
            answer = (
                f"Offline (ex‑GST): ₹{res['offline_sales']} Lakhs, "
                f"Online: ₹{res['online_sales']} Lakhs (GST: ₹{res['gst_amount']})."
            )

        else:
            answer = "Sorry, I don't know how to run that function."

    else:
        answer = msg.content

    st.session_state.history.append(("assistant", answer))
    st.session_state.history.append(("user", query))

for role, text in st.session_state.history:
    if role=="user":
        st.markdown(f"**Q:** {text}")
    else:
        st.markdown(f"**A:** {text}")
