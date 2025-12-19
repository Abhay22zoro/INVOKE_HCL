import sys
import os
import base64

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extraction.extract_pdf import chunk as chunks
from summarize_image import summarize_images



texts, tables, images = [], [], []

for chunk in chunks:
    chunk_type = type(chunk).__name__

    if chunk_type == "CompositeElement":
        texts.append(chunk)

        orig_elements = getattr(chunk.metadata, "orig_elements", [])

        for el in orig_elements:
            el_type = type(el).__name__

            if el_type == "Image":
                image_b64 = getattr(el.metadata, "image_base64", None)
                if image_b64:
                    images.append(image_b64)

            elif el_type == "Table":
                tables.append(el)


if images:
    with open("sample_image.jpg", "wb") as f:
        f.write(base64.b64decode(images[0]))
    print("\n🖼️ Image saved as 'sample_image.jpg' — open it to view.")

    # ✅ Run summarization
    summary = summarize_images([images[0]])[0]
    print("\n📝 Summary of Image[0]:\n", summary)
else:
    print("\nNo image found.")