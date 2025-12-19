# # rag_chain.py
# import sys
# import os
# from base64 import b64decode
# from langchain_core.runnables import RunnablePassthrough, RunnableLambda
# from langchain_core.output_parsers import StrOutputParser
# from perplexity_api import query_perplexity

# # Add the project root directory to the Python path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# # --------------------------
# # ✅ Preprocessor
# # --------------------------
# def parse_docs(docs):
#     b64, text = [], []
#     for doc in docs:
#         try:
#             b64decode(doc)
#             b64.append(doc)
#         except Exception:
#             text.append(doc)
#     return {"images": b64, "texts": text}

# # --------------------------
# # ✅ Prompt Builder
# # --------------------------
# def build_prompt(kwargs):
#     docs_by_type = kwargs["context"]
#     user_question = kwargs["question"]

#     context_text = "".join([t.page_content for t in docs_by_type["texts"]])

#     prompt_content = [
#         {
#             "type": "text",
#             "text": f"Answer the question based only on the following context.\nContext:\n{context_text}\nQuestion: {user_question}"
#         }
#     ]

#     for image in docs_by_type["images"]:
#         prompt_content.append({
#             "type": "image_url",
#             "image_url": {"url": f"data:image/jpeg;base64,{image}"}
#         })

#     return {
#         "model": "sonar",  # ✅ Use sonar model for Perplexity
#         "messages": [
#             {
#                 "role": "user",
#                 "content": prompt_content
#             }
#         ]
#     }

# # --------------------------
# # ✅ Perplexity Chain (Simple)
# # --------------------------
# def get_rag_chain(retriever):
#     return (
#         {
#             "context": retriever | RunnableLambda(parse_docs),
#             "question": RunnablePassthrough()
#         }
#         | RunnableLambda(build_prompt)
#         | RunnableLambda(query_perplexity)
#         | StrOutputParser()
#     )

# import uuid

# def save_image_if_relevant(image_b64, folder=".", prefix="matched_image"):
#     try:
#         image_data = b64decode(image_b64)
#         filename = os.path.join(folder, f"{prefix}_{uuid.uuid4().hex[:8]}.jpg")
#         with open(filename, "wb") as f:
#             f.write(image_data)
#         print(f"[INFO] Saved image: {filename}")
#     except Exception as e:
#         print(f"[ERROR] Failed to save image: {e}")


# # --------------------------
# # ✅ Perplexity Chain With Sources
# # --------------------------
# def get_rag_chain_with_sources(retriever):
#     def process_and_save(response_with_context):
#         # Extract context to get images
#         context = response_with_context.get("context", {})
#         images = context.get("images", [])
#         response = response_with_context["response"]

#         # Save first image if relevant (you can use a better filter)
#         if "image" in response.lower() and images:
#             save_image_if_relevant(images[0])  # Save only the first matching image

#         return response_with_context

#     return (
#         {
#             "context": retriever | RunnableLambda(parse_docs),
#             "question": RunnablePassthrough()
#         }
#         | RunnablePassthrough().assign(
#             response=(
#                 RunnableLambda(build_prompt)
#                 | RunnableLambda(query_perplexity)
#                 | StrOutputParser()
#             )
#         )
#         | RunnableLambda(process_and_save)
#     )


# rag_chain.py
import sys
import os
import uuid
from base64 import b64decode
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from perplexity_api import query_perplexity
import re

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# --------------------------------------------------
# ✅ Multi-question splitter
# --------------------------------------------------
def split_multi_question(query: str):
    if not isinstance(query, str):
        return [str(query)]

    separators = [" and ", " also ", " & ", ", and "," ? "," . "]
    pattern = "|".join(map(re.escape, separators))
    parts = re.split(pattern, query, flags=re.IGNORECASE)

    return [p.strip() for p in parts if len(p.strip()) > 5]


# --------------------------------------------------
# ✅ Multi-query vector retrieval
# --------------------------------------------------
def multi_query_retrieval(retriever, query, k=8):
    sub_questions = split_multi_question(query)

    all_docs = []
    for q in sub_questions:
        all_docs.extend(
            retriever.vectorstore.similarity_search(q, k=k)
        )

    # 🔹 Deduplicate by doc_id
    seen = set()
    unique_docs = []

    for doc in all_docs:
        doc_id = doc.metadata.get("doc_id")
        if doc_id not in seen:
            seen.add(doc_id)
            unique_docs.append(doc)

    return unique_docs


# --------------------------------------------------
# ✅ Image Save Utility
# --------------------------------------------------
def save_image_if_relevant(image_b64, folder="saved_images", prefix="matched_image"):
    try:
        os.makedirs(folder, exist_ok=True)

        if "," in image_b64:
            image_b64 = image_b64.split(",")[1]

        image_data = b64decode(image_b64)
        filename = os.path.join(folder, f"{prefix}_{uuid.uuid4().hex[:8]}.jpg")

        with open(filename, "wb") as f:
            f.write(image_data)

        print(f"[INFO] ✅ Image saved: {filename}")
    except Exception as e:
        print(f"[ERROR] ❌ Failed to save image: {e}")

# --------------------------------------------------
# ✅ Base64 Image Validator (STRICT)
# --------------------------------------------------
def is_valid_base64_image(b64_string: str, max_kb=500) -> bool:
    try:
        data = b64decode(b64_string, validate=True)
        return len(data) < max_kb * 1024
    except Exception:
        return False

# --------------------------------------------------
# ✅ SAFE QUERY (500 FALLBACK)
# --------------------------------------------------
def safe_query_perplexity(payload):
    try:
        return query_perplexity(payload)
    except RuntimeError as e:
        if "500" in str(e):
            print("[WARN] ⚠️ Perplexity 500 — retrying without images")

            payload["messages"][0]["content"] = [
                c for c in payload["messages"][0]["content"]
                if c["type"] != "image_url"
            ]
            return query_perplexity(payload)
        raise

# --------------------------------------------------
# ✅ Preprocessor (NO BASE64 IN TEXT EVER)
# --------------------------------------------------
def parse_docs(docs, docstore=None):
    images, texts = [], []

    for doc in docs:
        # --- Raw string case ---
        if isinstance(doc, str):
            if is_valid_base64_image(doc):
                images.append(doc)
            continue  # ❌ never treat raw strings as text

        # --- LangChain Document case ---
        doc_id = doc.metadata.get("doc_id")

        if doc_id and docstore:
            full_doc = docstore.mget([doc_id])[0]
            if not full_doc:
                continue
        else:
            full_doc = doc

        content = full_doc.page_content

        # --- Route correctly ---
        if isinstance(content, str) and is_valid_base64_image(content):
            images.append(content)
        else:
            texts.append(full_doc)

    return {"images": images, "texts": texts}

# --------------------------------------------------
# ✅ Prompt Builder (IMAGE-GATED, SAFE)
# --------------------------------------------------
def build_prompt(kwargs):
    docs_by_type = kwargs["context"]
    user_question = kwargs["question"]

    # --- SAFETY: normalize question ---
    if isinstance(user_question, dict):
        user_question = user_question.get("question", "")
    elif not isinstance(user_question, str):
        user_question = str(user_question)

    context_parts = []

    for doc in docs_by_type.get("texts", []):
        content = doc.page_content

        if isinstance(content, str) and "<table" in content.lower():
            context_parts.append(f"\n[TABLE]\n{content}\n[/TABLE]\n")
        else:
            context_parts.append(f"\n[TEXT]\n{content}\n[/TEXT]\n")

    context_text = "\n".join(context_parts)

    prompt_content = [
        {
            "type": "text",
            "text": (
                "Answer ALL parts of the question using ONLY the context provided below.\n"
                "If the question contains multiple sub-questions, address EACH part explicitly and completely.\n"
                "Present the answer in a formal, research-oriented manner, using separate paragraphs or clearly labeled sections where appropriate.\n"
                "If TABLES, figures, or structured data are present in the context, you MUST base your answer strictly on that data and maintain factual and numerical consistency.\n"
                "Do NOT use external knowledge, prior assumptions, or unstated scientific facts.\n"
                "Do NOT add citations, reference markers (e.g., [1], [2]), or speculative explanations.\n"
                "If any part of the question cannot be answered using the provided context alone, explicitly state that it cannot be determined from the given context.\n\n"

                f"Context:\n{context_text}\n\n"
                f"Question: {user_question}"
            )
        }
    ]

    # --- Include images ONLY if explicitly requested ---
    include_images = any(
        w in user_question.lower()
        for w in ["image", "diagram", "figure", "visual", "photo"]
    )

    if include_images:
        for image in docs_by_type.get("images", [])[:1]:  # max 1 image
            if is_valid_base64_image(image):
                prompt_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image}"
                    }
                })

    return {
        "model": "sonar",
        "messages": [{"role": "user", "content": prompt_content}]
    }

# --------------------------------------------------
# ✅ RAG Chain (TEXT-FIRST)
# --------------------------------------------------
def get_rag_chain(retriever):
    return (
        {
            "context": RunnableLambda(
                lambda x: parse_docs(
                    multi_query_retrieval(retriever, x["question"]),
                    retriever.docstore
                )
            ),
            "question": RunnablePassthrough()
        }
        | RunnableLambda(build_prompt)
        | RunnableLambda(safe_query_perplexity)
        | StrOutputParser()
    )

# --------------------------------------------------
# ✅ RAG Chain with source
# --------------------------------------------------

def get_rag_chain_with_sources(retriever):
    def process_and_save(response_with_context):
        context = response_with_context["context"]
        images = context.get("images", [])
        texts = context.get("texts", [])
        response = response_with_context["response"]

        print("\n🧠 [RESPONSE]:\n", response)

        print("\n📚 [TEXT CONTEXT]:")
        for i, doc in enumerate(texts):
            print(f"\n--- Text {i+1} ---")
            print(doc.page_content)

        if images:
            print(f"\n🖼️ [IMAGE CONTEXT]: {len(images)} image(s)")
            for i, img in enumerate(images):
                if is_valid_base64_image(img):
                    save_image_if_relevant(img, prefix=f"matched_image_{i}")

        return response_with_context

    return (
        {
            "context": RunnableLambda(
                lambda x: parse_docs(
                    multi_query_retrieval(retriever, x["question"]),
                    retriever.docstore
                )
            ),
            "question": RunnablePassthrough()
        }
        | RunnablePassthrough().assign(
            response=(
                RunnableLambda(build_prompt)
                | RunnableLambda(safe_query_perplexity)
                | StrOutputParser()
            )
        )
        | RunnableLambda(process_and_save)
    )

