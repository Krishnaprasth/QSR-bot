import pandas as pd
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

def ingest_csv_to_faiss(csv_path: str, index_path: str):
    df = pd.read_csv(csv_path)
    chunks = []
    for _, row in df.iterrows():
        text = (
            f"Store: {row['Store']}; Month: {row['Month']}; "
            + "; ".join(f"{col}: {row[col]}" for col in df.columns if col not in ['Store','Month'])
        )
        chunks.append(text)
    embeddings = OpenAIEmbeddings()
    faiss_index = FAISS.from_texts(chunks, embeddings)
    faiss_index.save_local(index_path)

if __name__ == "__main__":
    ingest_csv_to_faiss("sales_data.csv", "faiss_index")