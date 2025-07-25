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
            st.write(f"**Columns:** {', '.join(df.columns)}")
    
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

# Helper function to create data context for AI
def create_data_context(df):
    """Create a concise summary of the data for AI context"""
    context = f"""
    Sales Data Summary:
    - Total Rows: {len(df)}
    - Columns: {', '.join(df.columns)}
    - Unique Stores: {df['Store'].nunique() if 'Store' in df.columns else 'N/A'}
    - Unique Metrics: {', '.join(df['Metric'].unique()) if 'Metric' in df.columns else 'N/A'}
    
    The data contains store-wise monthly metrics including sales, costs, and other operational metrics.
    GST is 5% for offline stores and 0% for online stores.
    """
    return context

# Function to analyze query with AI
def analyze_with_ai(query, data_context, api_provider, api_key):
    """Send query to AI and get analysis"""
    
    prompt = f"""
    You are a sales analytics expert. Analyze the following sales data and answer the user's question.
    
    {data_context}
    
    User Question: {query}
    
    Please provide:
    1. A clear answer to the question
    2. Any relevant calculations
    3. Format numbers as lakhs (e.g., ₹12.5 Lakhs)
    """
    
    try:
        if "OpenAI" in api_provider:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful sales analytics assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        else:
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"

# Main app
st.title("🤖 AI Sales Analytics Bot")
st.markdown("Ask questions about your sales data in natural language")

# Check if configuration is complete
if not api_key:
    st.warning("⚠️ Please configure your API key in the sidebar")
elif st.session_state.data is None:
    st.error("📊 Error loading data. Please check if sales_data.csv exists")
else:
    # Chat interface
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about SSG, store performance, trends..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                # Create data context
                data_context = create_data_context(st.session_state.data)
                
                # Get AI analysis
                response = analyze_with_ai(prompt, data_context, api_provider, api_key)
                st.write(response)
                
                # Save assistant message
                st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>This bot uses AI to analyze your sales data. Configure your API key and upload data to start.</p>
</div>
""", unsafe_allow_html=True)
