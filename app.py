import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import json
from openai import OpenAI
from kpi import (
    generate_report,
    generate_vintage_report,
    split_online_offline,
    get_top_sales_by_month,
    get_revenue_breakup_by_cohort_by_fy,
    get_overall_ssg_by_fy,
    run_aggregation,
    run_trend,
    run_comparison,
    run_anomaly_detection,
    run_stat_test
)
from utils import load_data
from intent_manager import IntentManager

# Load data
df = load_data()

# Initialize OpenAI and Intent Manager
openai = OpenAI()
intent_mgr = IntentManager(openai)

# Define function-calling schemas (generic + specific)
functions = [
    {
        "name": "run_aggregation",
        "description": "Aggregate a metric by given dimensions",
        "parameters": {
            "type": "object",
            "properties": {
                "metric": {"type": "string"},
                "aggfunc": {"type": "string", "enum": ["sum", "mean", "count", "median"]},
                "by": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["metric", "aggfunc"]
        }
    },
    {
        "name": "run_trend",
        "description": "Compute a time series of a metric",
        "parameters": {
            "type": "object",
            "properties": {
                "metric": {"type": "string"},
                "group_by": {"type": "array", "items": {"type": "string"}},
                "window": {"type": "integer", "default": 1}
            },
            "required": ["metric"]
        }
    },
    {
        "name": "run_comparison",
        "description": "Compare metrics between two entities",
        "parameters": {
            "type": "object",
            "properties": {
                "entity_type": {"type": "string"},
                "entity1": {"type": "string"},
                "entity2": {"type": "string"},
                "metric": {"type": "string"}
            },
            "required": ["entity_type", "entity1", "entity2", "metric"]
        }
    },
    {
        "name": "run_anomaly_detection",
        "description": "Detect anomalies in a time series",
        "parameters": {
            "type": "object",
            "properties": {
                "metric": {"type": "string"},
                "group_by": {"type": "array", "items": {"type": "string"}},
                "method": {"type": "string", "enum": ["zscore", "iqr"]},
                "threshold": {"type": "number"}
            },
            "required": ["metric", "method", "threshold"]
        }
    },
    {
        "name": "run_stat_test",
        "description": "Run a statistical test or correlation between two metrics",
        "parameters": {
            "type": "object",
            "properties": {
                "metric_x": {"type": "string"},
                "metric_y": {"type": "string"},
                "test": {"type": "string", "enum": ["pearson", "spearman", "ttest"]}
            },
            "required": ["metric_x", "metric_y", "test"]
        }
    },
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
    },
    {
        "name": "get_top_sales_by_month",
        "description": "Return the store with highest net sales for a given month and FY",
        "parameters": {
            "type": "object",
            "properties": {"month": {"type": "string"}, "fy": {"type": "string"}},
            "required": ["month", "fy"]
        }
    },
    {
        "name": "get_revenue_breakup_by_cohort_by_fy",
        "description": "Compute total Net Sales by FY for specified store cohorts",
        "parameters": {
            "type": "object",
            "properties": {"cohorts": {"type": "array", "items": {"type": "string"}}},
            "required": ["cohorts"]
        }
    },
    {
        "name": "get_overall_ssg_by_fy",
        "description": "Compute overall Same-Store Sales Growth (SSG) for a fiscal year",
        "parameters": {
            "type": "object",
            "properties": {"fy": {"type": "string"}},
            "required": ["fy"]
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
        name, args = msg.function_call.name, msg.function_call.arguments
        if isinstance(args, str):
            args = json.loads(args)
        # Dispatch logic omitted for brevity...
        # Use run_aggregation, run_trend, etc. based on name
        answer = f"Function {name} executed."
    else:
        answer = msg.content

    st.session_state.history.append(("assistant", answer))
    st.session_state.history.append(("user", query))

for role, text in st.session_state.history:
    st.markdown(f"**{role.title()}:** {text}")
