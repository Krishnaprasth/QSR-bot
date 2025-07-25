# app.py - Updated version with auto-loading data
import streamlit as st
import pandas as pd
import numpy as np
from openai import OpenAI
import anthropic
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Sales Analytics Bot",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'data' not in st.session_state:
    st.session_state.data = None

# Auto-load sales data
@st.cache_data
def load_sales_data():
    try:
        df = pd.read_csv('sales_data.csv')
        # Add calculated columns
        df['Year'] = df['Month'].str.split('-').str[0].astype(int)
        df['MonthName'] = df['Month'].str.split('-').str[1]
        # Add GST calculations
        df['IsOnline'] = df['Store'].str.contains('ONLINE|WEB|APP', case=False, na=False)
        df['GSTRate'] = df['IsOnline'].apply(lambda x: 0 if x else 0.05)
        df['GSTAmount'] = df.apply(lambda row: row['Amount'] * row['GSTRate'] 
                                   if row['Metric'] in ['Gross Sales', 'Net Sales'] else 0, axis=1)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Load data on startup
if st.session_state.data is None:
    st.session_state.data = load_sales_data()

# Sidebar for configuration
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Show data status
    if st.session_state.data is not None:
        st.success(f"✅ Data Loaded: {len(st.session_state.data):,} rows")
        with st.expander("Data Info"):
            df = st.session_state.data
            st.write(f"**Date Range:** {df['Month'].min()} to {df['Month'].max()}")
            st.write(f"**Stores:** {df['Store'].nunique()}")
            st.write(f"**Metrics:** {', '.join(df['Metric'].unique()[:5])}...")
    
    st.markdown("---")
    
    # API Provider selection
    api_provider = st.selectbox(
        "Select AI Provider",
        ["OpenAI (GPT-4)", "Anthropic (Claude)"]
    )
    
    # API Key input
    if api_provider == "OpenAI (GPT-4)":
        api_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    else:
        api_key = st.text_input("Anthropic API Key", type="password", value=os.getenv("ANTHROPIC_API_KEY", ""))

# Rest of the app.py code remains the same...
# (Copy the rest from the original app.py artifact)
