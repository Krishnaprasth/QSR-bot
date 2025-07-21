import streamlit as st
import pandas as pd
from query_router import route_query
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="QSR CEO Bot", layout="wide")
st.title("QSR CEO Performance Bot")

@st.cache_data
def load_data():
    return pd.read_csv("QSR_CEO_CLEANED_FY22_TO_FY26_FULL_FINAL.csv")

df = load_data()

# Download helpers
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Results')
    output.seek(0)
    return output

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def convert_df_to_txt(df):
    return df.to_string(index=False).encode('utf-8')

def convert_df_to_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    col_width = pdf.w / (len(df.columns) + 1)
    row_height = 10
    for col in df.columns:
        pdf.cell(col_width, row_height, col, border=1)
    pdf.ln(row_height)
    for _, row in df.iterrows():
        for item in row:
            pdf.cell(col_width, row_height, str(item), border=1)
        pdf.ln(row_height)
    output = BytesIO()
    pdf.output(output)
    output.seek(0)
    return output

query = st.text_input("Ask a performance question:")

if query:
    response = route_query(query, df)
    if response is not None:
        st.success("Answered via logic engine")
        st.dataframe(response)

        # Visualizations
        if "Month-Year" in response.columns and "Amount (in lakhs)" in response.columns:
            st.line_chart(response.set_index("Month-Year"))
        elif "Store" in response.columns and "Amount (in lakhs)" in response.columns:
            st.bar_chart(response.set_index("Store"))

        # Download buttons
        st.download_button("📥 Excel", convert_df_to_excel(response), "output.xlsx")
        st.download_button("📄 CSV", convert_df_to_csv(response), "output.csv")
        st.download_button("📝 Text", convert_df_to_txt(response), "output.txt")
        st.download_button("📘 PDF", convert_df_to_pdf(response), "output.pdf")
    else:
        st.warning("Query not recognized. Please rephrase or refine.")