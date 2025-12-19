# import streamlit as st
# import sys
# import os
# import logging
# from tempfile import NamedTemporaryFile

# # Ensure the root directory is in the path so backend modules can be imported
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# # 🧠 RAG and summary modules
# from extraction.extract_pdf import extract_pdf_elements
# from summarization.summarize_text_table import summarize_texts, summarize_tables
# from summarization.summarize_image import summarize_images
# from rag.vector_store import get_vectorstore
# from rag.retrieval import setup_retriever, store_documents
# from rag.rag_chain import get_rag_chain, get_rag_chain_with_sources
# from perplexity_api import query_perplexity

# # --- Streamlit Page Config ---
# st.set_page_config(page_title="MultiModal RAG", layout="centered")
# st.title("📄 MultiModal PDF QA App")

# # --- File Upload ---
# uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

# # --- Query Input ---
# query = st.text_input("Ask a question:")

# # --- RAG Mode Selection (shown only if a file is uploaded) ---
# rag_mode = None
# if uploaded_file:
#     rag_mode = st.radio("Select RAG Mode", ["Only response", "Response and source"])

# # --- Submit Button ---
# submit = st.button("Submit")

# # --- PDF Processor Function (previously in backend/api.py) ---
# def process_pdf(file_path_or_bytes):
#     if isinstance(file_path_or_bytes, bytes):
#         with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#             tmp.write(file_path_or_bytes)
#             file_path = tmp.name
#     else:
#         file_path = file_path_or_bytes

#     st.info("📚 Chunking PDF into smaller sections...")
#     chunks = extract_pdf_elements(file_path)

#     st.info("🧩 Splitting chunks into text, tables, and images...")
#     texts, tables, images = [], [], []
#     for chunk in chunks:
#         if type(chunk).__name__ == "CompositeElement":
#             texts.append(chunk)
#             orig_elements = getattr(chunk.metadata, "orig_elements", [])
#             for el in orig_elements:
#                 el_type = type(el).__name__
#                 if el_type == "Image":
#                     image_b64 = getattr(el.metadata, "image_base64", None)
#                     if image_b64:
#                         images.append(image_b64)
#                 elif el_type == "Table":
#                     tables.append(el)

#     st.info("📝 Preparing semantic summaries for each chunk...")
#     text_summaries = summarize_texts([t.text for t in texts])
#     table_summaries = summarize_tables([t.metadata.text_as_html for t in tables])
#     image_summaries = summarize_images(images)

#     print(len(text_summaries))
#     print(len(table_summaries))
#     print(len(image_summaries))

#     st.info("🗂️ Setting up the vector store with embeddings...")
#     vectorstore = get_vectorstore()
#     retriever = setup_retriever(vectorstore)

#     st.info("💾 Storing processed data into the database...")
#     store_documents(retriever, texts, text_summaries, "doc_id")
#     store_documents(retriever, tables, table_summaries, "doc_id")
#     store_documents(retriever, images, image_summaries, "doc_id")

#     return retriever

# # --- Main Logic ---
# if submit and query:
#     if uploaded_file:
#         st.info("🔧 Processing PDF and preparing vector store...")
#         retriever = process_pdf(uploaded_file.read())

#         st.info("🧠 Generating answer using selected RAG mode...")
#         if rag_mode == "Only response":
#             chain = get_rag_chain(retriever)
#             result = chain.invoke({"question": query})
#             st.success("✅ Response:")
#             st.markdown(result)

#         else:  # "Response and source"
#             chain = get_rag_chain_with_sources(retriever)
#             output = chain.invoke({"question": query})

#             response = output.get("response", "")
#             context = output.get("context", {})

#             # Display the response
#             st.success("✅ Response:")
#             st.markdown(response)

#             # Display textual context
#             text_context = context.get("texts", [])
#             if text_context:
#                 st.info("📚 Context (Text):")
#                 for i, doc in enumerate(text_context):
#                     try:
#                         content = doc.page_content
#                     except:
#                         content = str(doc)
#                     st.markdown(f"**Document {i+1}:**\n{content}")

#             # Display image context
#             image_context = context.get("images", [])
#             if image_context:
#                 st.info("🖼️ Context (Images):")
#                 for i, img_b64 in enumerate(image_context):
#                     if "," in img_b64:
#                         img_b64 = img_b64.split(",")[1]  # Strip data URI prefix
#                     st.image(f"data:image/jpeg;base64,{img_b64}", caption=f"Image {i+1}")

#     else:
#         # No file uploaded: fallback to Groq model
#         st.info("💬 No document provided. Using direct LLM query...")
#         payload = {
#             "model": "sonar",
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": [{"type": "text", "text": query}]
#                 }
#             ]
#         }
#         result = query_perplexity(payload)
#         st.success("✅ Response:")
#         st.markdown(result)



import streamlit as st
import sys
import os
from tempfile import NamedTemporaryFile

# Ensure local imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extraction.extract_pdf import extract_pdf_elements
from extraction.extract_docx import extract_docx_elements
from summarization.summarize_text_table import summarize_texts, summarize_tables
from summarization.summarize_image import summarize_images
from rag.vector_store import get_vectorstore
from rag.retrieval import setup_retriever, store_documents
from rag.rag_chain import get_rag_chain, get_rag_chain_with_sources
from perplexity_api import query_perplexity

# --- Streamlit Page Config ---
st.set_page_config(page_title="MultiModal RAG", layout="centered")
st.title("📄 Intelligent Document Understanding with Multimodal RAG")

# --- Session State ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "retriever" not in st.session_state:
    st.session_state.retriever = None

if "docs_uploaded" not in st.session_state:
    st.session_state.docs_uploaded = False

# --- File Upload ---
uploaded_files = st.file_uploader(
    "Upload 3–5 PDF or DOCX files",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

query = st.text_input("Ask a question:")
rag_mode = st.radio(
    "Select RAG Mode",
    ["Only response", "Response and source"]
) if uploaded_files else None
submit = st.button("Submit")

# -------------------------------------------------
# MULTI-DOCUMENT PROCESSING (ALIGNED WITH main.py)
# -------------------------------------------------
def process_documents(uploaded_files):
    texts, tables, images = [], [], []

    for uploaded_file in uploaded_files:
        suffix = os.path.splitext(uploaded_file.name)[1].lower()

        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            file_path = tmp.name

        st.info(f"📄 Processing {uploaded_file.name}")

        # ---- Extract ----
        if suffix == ".pdf":
            chunks = extract_pdf_elements(file_path)
        elif suffix == ".docx":
            chunks = extract_docx_elements(file_path)
        else:
            continue

        # ---- Unified parsing (SAME AS main.py) ----
        for chunk in chunks:
            chunk_type = type(chunk).__name__

            # ---------------- TEXT ----------------
            if chunk_type in ["CompositeElement", "NarrativeText", "Title", "ListItem"]:
                text = getattr(chunk, "text", "").strip()
                if not text:
                    continue

                # PDF-specific
                if chunk_type == "CompositeElement":
                    orig_elements = getattr(chunk.metadata, "orig_elements", [])

                    has_table = any(type(el).__name__ == "Table" for el in orig_elements)
                    is_table_like_text = (
                        text.count("|") > 3 or
                        "BLEU" in text or
                        "Training Cost" in text
                    )

                    if not has_table and not is_table_like_text:
                        texts.append(chunk)

                    for el in orig_elements:
                        if type(el).__name__ == "Table":
                            tables.append(el)
                        elif type(el).__name__ == "Image":
                            image_b64 = getattr(el.metadata, "image_base64", None)
                            if image_b64:
                                images.append(image_b64)

                # DOCX text
                else:
                    texts.append(chunk)

            # ---------------- TABLE (DOCX) ----------------
            elif chunk_type == "Table":
                tables.append(chunk)

            # ---------------- IMAGE (DOCX) ----------------
            elif chunk_type == "Image":
                image_b64 = getattr(chunk.metadata, "image_base64", None)
                if image_b64:
                    images.append(image_b64)

    # ---- Summaries ----
    st.info("📝 Generating summaries...")
    text_summaries = summarize_texts([t.text for t in texts])
    table_summaries = summarize_tables([t.metadata.text_as_html for t in tables])
    image_summaries = summarize_images(images)

    # ---- Vector Store ----
    vectorstore = get_vectorstore()
    retriever = setup_retriever(vectorstore)

    st.info("💾 Storing data...")

    if text_summaries:
        store_documents(retriever, texts, text_summaries, "doc_id")

    if table_summaries:
        store_documents(retriever, tables, table_summaries, "doc_id")

    if image_summaries:
        store_documents(retriever, images, image_summaries, "doc_id")

    return retriever

# -------------------------------------------------
# SUBMIT LOGIC
# -------------------------------------------------
if submit and query:
    if uploaded_files and not st.session_state.docs_uploaded:
        st.session_state.retriever = process_documents(uploaded_files)
        st.session_state.docs_uploaded = True
        st.success("✅ Documents processed and stored!")

    retriever = st.session_state.retriever

    if uploaded_files:
        if rag_mode == "Only response":
            chain = get_rag_chain(retriever)
            response = chain.invoke({"question": query})
            sources = None
        else:
            chain = get_rag_chain_with_sources(retriever)
            output = chain.invoke({"question": query})
            response = output.get("response", "")
            sources = output.get("context", {})

        st.session_state.chat_history.append(("user", query))
        st.session_state.chat_history.append(("assistant", response))

        st.success("✅ Response:")
        st.markdown(response)

        # ---------- SOURCE DISPLAY ----------
        if sources:
            text_ctx = sources.get("texts", [])
            img_ctx = sources.get("images", [])

            normal_texts, table_texts = [], []

            for doc in text_ctx:
                content = doc.page_content
                if "<table" in content.lower():
                    table_texts.append((doc, content))
                else:
                    normal_texts.append((doc, content))

            # Deduplicate
            seen = set()
            unique_texts = []
            for doc, content in normal_texts:
                key = (doc.metadata.get("page"), content[:120])
                if key not in seen:
                    seen.add(key)
                    unique_texts.append((doc, content))

            if unique_texts:
                st.info("📚 Context (Text)")
                for i, (doc, content) in enumerate(unique_texts):
                    page = doc.metadata.get("page")
                    page_info = f"(Page {page})" if page is not None else ""
                    st.markdown(f"**Text {i+1} {page_info}:**\n{content}")

            if table_texts:
                st.info("📊 Context (Tables)")
                for i, (doc, table_html) in enumerate(table_texts):
                    page = doc.metadata.get("page")
                    page_info = f"(Page {page})" if page is not None else ""
                    st.markdown(f"**Table {i+1} {page_info}:**", unsafe_allow_html=True)
                    st.markdown(table_html, unsafe_allow_html=True)

            if img_ctx:
                st.info("🖼️ Context (Images)")
                for i, img_b64 in enumerate(img_ctx):
                    if "," in img_b64:
                        img_b64 = img_b64.split(",")[1]
                    st.image(
                        f"data:image/jpeg;base64,{img_b64}",
                        caption=f"Image {i+1}"
                    )

# -------------------------------------------------
# CHAT HISTORY
# -------------------------------------------------
if st.session_state.chat_history:
    st.markdown("---")
    st.subheader("🕘 Chat History")

    for role, msg in st.session_state.chat_history:
        if role == "user":
            st.markdown(f"**🧑 You:** {msg}")
        else:
            first_line = msg.strip().split("\n")[0]
            with st.expander(f"🤖 Assistant: {first_line}"):
                st.markdown(msg)
