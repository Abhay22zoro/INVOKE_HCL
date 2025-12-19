# test_retrieval.py

from vector_store import get_vectorstore
from retrieval import setup_retriever, store_documents

def test_retrieval():
    # Sample test data
    texts = [
        "LangChain is a framework for developing LLM-powered applications.",
        "Transformers are powerful deep learning models."
    ]
    summaries = [
        "LangChain summary",
        "Transformer summary"
    ]
    query = "What are transformers?"

    # Get vector store and setup retriever
    vectorstore = get_vectorstore()
    retriever = setup_retriever(vectorstore)

    # Store documents
    store_documents(retriever, texts, summaries, id_key="doc_id")

    # Perform a retrieval query
    results = retriever.get_relevant_documents(query)

    print("\n🔍 Relevant documents:\n")
    for doc in results:
        print(f"📄 Content: {doc.page_content}")
        print(f"📎 Metadata: {doc.metadata}\n")

if __name__ == "__main__":
    test_retrieval()
