from unstructured.partition.docx import partition_docx

def extract_docx_elements(file_path: str):
    elements = partition_docx(
        filename=file_path,
        infer_table_structure=True,
        extract_image_block_types=["Image"],
        extract_image_block_to_payload=True
    )
    return elements
