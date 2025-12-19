# import sys
# import os

# # Add the project root directory to the Python path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from extraction.extract_pdf import chunk as chunks
# from summarize_text_table import summarize_tables, summarize_texts



# texts, tables, images = [], [], []

# for chunk in chunks:
#     chunk_type = type(chunk).__name__

#     if chunk_type == "CompositeElement":
#         texts.append(chunk)

#         orig_elements = getattr(chunk.metadata, "orig_elements", [])

#         for el in orig_elements:
#             el_type = type(el).__name__

#             if el_type == "Image":
#                 image_b64 = getattr(el.metadata, "image_base64", None)
#                 if image_b64:
#                     images.append(image_b64)

#             elif el_type == "Table":
#                 tables.append(el)


# if texts:
#     print("📝 Original Text:\n", texts[0].text)
#     summary = summarize_texts([texts[0]])
#     print("🔍 Summary:\n", summary[0])
# else:
#     print("No text elements found.")

# if tables:
#     print("📊 Original Table (HTML):\n", tables[0].metadata.text_as_html)
#     summary = summarize_tables([tables[0].metadata.text_as_html])
#     print("🔍 Table Summary:\n", summary[0])
# else:
#     print("No table elements found.")

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extraction.extract_pdf import extract_pdf_elements
from summarization.summarize_text_table import summarize_tables, summarize_texts

# Load PDF properly (❗ NOT from global chunk variable)
file_path = "./data/table.pdf"
chunks = extract_pdf_elements(file_path)

texts, tables = [], []

for chunk in chunks:
    if type(chunk).__name__ == "CompositeElement":
        texts.append(chunk)
        for el in getattr(chunk.metadata, "orig_elements", []):
            if type(el).__name__ == "Table":
                tables.append(el)

print(f"Texts found: {len(texts)}")
print(f"Tables found: {len(tables)}")

# ---- TEXT SUMMARY CHECK ----
if texts:
    text_input = texts[0].text
    text_summary = summarize_texts([text_input])
    print("\n📝 TEXT SUMMARY:\n", text_summary[0])

# ---- TABLE SUMMARY CHECK ----
if tables:
    table_html = tables[0].metadata.text_as_html
    table_summary = summarize_tables([table_html])
    print("\n📊 TABLE SUMMARY:\n", table_summary[0])
else:
    print("❌ No tables detected in PDF")
