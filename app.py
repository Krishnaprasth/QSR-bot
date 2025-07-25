import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sales Analytics Bot", layout="wide")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv('sales_data.csv')

data = load_data()

st.title("🤖 Sales Analytics Bot")
st.write(f"Loaded {len(data):,} rows of sales data")

# Chat interface
if 'messages' not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Ask about your sales data..."):
    st.chat_message("user").write(prompt)
    
    with st.chat_message("assistant"):
        # Analyze based on keywords
        if "highest sales" in prompt.lower() and "march 2025" in prompt.lower():
            march_data = data[(data['Month'] == '2025-Mar') & (data['Metric'] == 'Gross Sales')]
            store_sales = march_data.groupby('Store')['Amount'].sum().sort_values(ascending=False)
            
            if len(store_sales) > 0:
                response = f"**{store_sales.index[0]}** had the highest sales in March 2025 with ₹{store_sales.iloc[0]:.2f} Lakhs"
            else:
                response = "No sales data found for March 2025"
        else:
            response = "I can analyze: highest sales by month, store performance, metrics comparison, etc."
        
        st.write(response)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": response})
