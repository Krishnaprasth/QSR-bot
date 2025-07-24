import pandas as pd
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

def ingest(csv_path: str = "sales_data.csv", index_path: str = "faiss_index"):
    df = pd.read_csv(csv_path)
    texts = []
    for _, row in df.iterrows():
        texts.append(
            f"Store: {row['Store']}; Month: {row['Month']}; "
            + "; ".join(f"{col}: {row[col]}" for col in df.columns if col not in ['Store','Month'])
        )
    embeddings = OpenAIEmbeddings()
    faiss_index = FAISS.from_texts(texts, embeddings)
    faiss_index.save_local(index_path)

if __name__ == "__main__":
    ingest()
