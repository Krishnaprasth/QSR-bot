from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

class VectorRetriever:
    def __init__(self, index_path: str):
        embeddings = OpenAIEmbeddings()
        self.vector_store = FAISS.load_local(index_path, embeddings)

    def retrieve(self, query: str, top_k: int = 5):
        results = self.vector_store.as_retriever(search_kwargs={"k": top_k}).get_relevant_documents(query)
        return [(doc.page_content, doc.score) for doc in results]
