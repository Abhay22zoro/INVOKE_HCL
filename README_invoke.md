#  Research-Oriented RAG Assistant

An **interactive, research-focused Retrieval-Augmented Generation (RAG) system** designed to answer **document-grounded questions** from **3–5 uploaded PDF or DOCX files**.  
The system emphasizes **accurate retrieval, controlled generation, and explainable design choices**, making it suitable for academic and evaluation settings.

---

## Project Objective

The primary goal of this project is to demonstrate a **clear understanding of the end-to-end RAG workflow**, including:
- How documents are ingested, processed, and indexed
- How semantic retrieval improves answer quality
- How LLMs should be used as *reasoning engines*, not knowledge stores
- How GenAI components integrate into a deployable system

---

## High-Level Idea (Why RAG?)

Large Language Models alone may hallucinate or provide outdated information.  
This project uses **Retrieval-Augmented Generation** to:
- Ground answers in uploaded documents
- Reduce hallucinations
- Enable dynamic knowledge updates without retraining models

---

## 🔄 End-to-End Workflow (Step-by-Step)

```
1. User uploads 3–5 research documents (PDF / DOCX)
        ↓
2. Text extraction using OCR-aware and structured parsers
        ↓
3. Semantic chunking of documents
        ↓
4. Conversion of chunks into dense vector embeddings
        ↓
5. Storage of embeddings in a vector database
        ↓
6. User submits a natural language query
        ↓
7. Similarity-based retrieval of top-K relevant chunks
        ↓
8. Dynamic prompt construction using retrieved context
        ↓
9. LLM generates a grounded, context-aware response
```

Each stage is modular, making the pipeline easy to debug, extend, and deploy.

---

### Current workflow
  
![RAG Workflow Diagram](rag.svg)



## Technology Stack & Design Rationale

### 🔹 Frontend
- **Streamlit**  
  Enables rapid development of interactive data and ML applications with minimal frontend complexity, ideal for demos and evaluations.

---

### 🔹 Document Ingestion
- **Amazon Textract**  
  Used for robust OCR and structured text extraction from scanned or complex PDFs where traditional parsers often fail.

- **python-docx**  
  Lightweight and reliable library for extracting structured text from DOCX files.

---

### 🔹 Text Chunking
- **RecursiveCharacterTextSplitter (LangChain)**  
  Splits documents hierarchically using semantic separators (paragraphs, sentences), preserving context better than fixed-size chunking.

---

### 🔹 Embeddings
- **Sentence Transformers (e.g.,sentence-transformers/all-MiniLM-L6-v2)**  
  Generates dense semantic embeddings that capture contextual meaning, enabling effective similarity search for retrieval tasks.

---

### 🔹 Vector Database
- **ChromaDB**  
  Chosen for its local persistence, fast similarity search, and tight integration with LangChain well suited for research prototypes.

---

### 🔹 Retrieval & Orchestration
- **LangChain**  
  Provides abstractions for retrievers, chains, and prompt templates, enabling a clean and modular RAG pipeline.

---

### 🔹 Prompt Engineering
- **Dynamic Prompt Templates**  
  Prompts are constructed at runtime using retrieved context, ensuring that LLM responses are strictly grounded in document evidence.

---

### 🔹 Output Validation
- **Pydantic**  
  Enforces structured and validated outputs, improving reliability and making the system more production-ready.

---

### 🔹 Large Language Model
- **ChatGPT / Open-source LLM**  
  Used only for response generation and reasoning, not for storing factual knowledge.

---

##  Supported Input Formats

-  PDF  [ACCEPTED]
-  DOCX [ACCEPTED]  
-  Other formats are excluded intentionally to maintain research-document focus

---


##  Key Design Decisions

- **RAG over fine-tuning**: Faster iteration and dynamic updates without retraining  
- **OCR-first ingestion**: Handles real-world academic and scanned documents  
- **Semantic chunking**: Improves retrieval precision and answer coherence  
- **Vector similarity search**: Enables meaning-based retrieval instead of keyword matching  

---

##  Challenges & Learnings

- Document structure loss during OCR
    Learning: Layout-agnostic chunking and clear prompt grounding helped compensate for missing headings and formatting cues.

- Over-retrieval introduced contextual noise
    Learning: Limiting top-k retrieval and prioritizing precision produced more accurate responses than increasing context volume.

- Insufficient metadata hindered traceability
    Learning: Adding minimal metadata (source file and chunk index) significantly improved debugging and answer explainability.

- Vector store persistence required index management
    Learning: Persistent embeddings improved efficiency but necessitated explicit re-ingestion when documents changed to avoid stale results.

---

##  Outcome

The system reliably answers **research-style questions** by retrieving relevant document context and generating grounded responses.  
It demonstrates a **clear, interview-ready understanding of RAG system design and trade-offs**.

---

##  Future Work & Enhancements

- **Multimodal RAG**: Incorporating images, tables, and charts alongside text  
- **Multi-Query Retrieval**: Generating multiple reformulated queries to improve recall  
- Source citation highlighting at chunk level  
- Cloud Deployment 

---

This project serves as a strong foundation for building **scalable, reliable, and research-oriented GenAI applications**.
