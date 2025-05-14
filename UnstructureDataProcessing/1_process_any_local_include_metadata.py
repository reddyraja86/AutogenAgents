import json
import os
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx
from unstructured.partition.pptx import partition_pptx
from unstructured.partition.text import partition_text
from unstructured.partition.image import partition_image
from unstructured.partition.html import partition_html

# Add more as needed...

input_filepath = "../pdfs/test.txt"

ext = os.path.splitext(input_filepath)[-1].lower()

# Decide which partitioner to use
if ext == ".pdf":
    elements = partition_pdf(filename=input_filepath)
elif ext == ".docx":
    elements = partition_docx(filename=input_filepath)
elif ext == ".pptx":
    elements = partition_pptx(filename=input_filepath)
elif ext == ".txt":
    elements = partition_text(filename=input_filepath)
elif ext in [".jpg", ".jpeg", ".png"]:
    elements = partition_image(filename=input_filepath)
elif ext == ".html":
    elements = partition_html(filename=input_filepath)
else:
    raise ValueError(f"Unsupported file extension: {ext}")

# Convert to dicts
element_dicts = [el.to_dict() for el in elements]

# Print as JSON
print(json.dumps(element_dicts, indent=2))
