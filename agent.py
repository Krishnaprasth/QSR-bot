from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA

def load_agent(index_path: str):
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.load_local(index_path, embeddings)
    llm = ChatOpenAI(temperature=0.2)
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="map_reduce",
        retriever=vector_store.as_retriever(search_kwargs={"k":5}")
    )
    return qa

if __name__ == "__main__":
    qa = load_agent("faiss_index")
    print("RAG agent ready. Ask questions below:")
    while True:
        query = input("📝 Your question (or 'exit'): ")
        if query.lower() in ("exit", "quit"):
            break
        answer = qa.run(query)
        print("\n🤖 Answer:\n", answer)