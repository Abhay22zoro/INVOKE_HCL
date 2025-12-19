from langchain.storage import InMemoryStore
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.schema import Document
import uuid


def store_documents(retriever, elements, summaries, id_key):
    ids = [str(uuid.uuid4()) for _ in elements]

    # -------------------------------
    # Store SUMMARY docs in vector DB
    # -------------------------------
    summary_docs = [
        Document(
            page_content=summaries[i],
            metadata={id_key: ids[i]}
        )
        for i in range(len(summaries))
        if summaries[i] and summaries[i].strip()
    ]

    if not summary_docs:
        raise ValueError("❌ No valid summaries to store. All were empty or invalid.")

    retriever.vectorstore.add_documents(summary_docs)

    # ---------------------------------
    # Store ORIGINAL docs in docstore
    # WITH ROBUST PAGE EXTRACTION
    # ---------------------------------
    docstore_entries = []

    for i in range(len(elements)):
        element = elements[i]

        # ✅ Robust page number extraction
        page_number = None
        try:
            if hasattr(element.metadata, "page_number"):
                page_number = element.metadata.page_number
            elif hasattr(element.metadata, "page_numbers"):
                page_number = element.metadata.page_numbers[0]
        except Exception:
            pass

        docstore_entries.append(
            (
                ids[i],
                Document(
                    page_content=getattr(element, "text", str(element)),
                    metadata={
                        id_key: ids[i],
                        "page": page_number
                    }
                )
            )
        )

    retriever.docstore.mset(docstore_entries)


def setup_retriever(vectorstore):
    store = InMemoryStore()
    retriever = MultiVectorRetriever(
        vectorstore=vectorstore,
        docstore=store,
        id_key="doc_id"
    )
    return retriever
