
from unstructured.partition.pdf import partition_pdf
import json

input_filepath = "../pdfs/OTC-DictionaryAPI.pdf"
print(f"🔵 Reading PDF filerrrrrrrrr: {input_filepath}")
# Partition the PDF
elements = partition_pdf(filename=input_filepath)

sections = []
current_section = None

for el in elements:
    el_dict = el.to_dict()
    el_type = el_dict["type"]
    el_text = el_dict.get("text", "").strip()

    if not el_text:
        continue  # Skip empty or whitespace-only text

    # Start new section for Titles and Headers
    if el_type in ["Title", "Header"]:
        current_section = {
            "section_title": el_text,
            "content": []
        }
        sections.append(current_section)

    # ListItem, NarrativeText, etc. go into current section
    elif el_type in ["NarrativeText", "ListItem", "Table", "FigureCaption"]:
        if current_section is None:
            # If no title yet, create a default one
            current_section = {
                "section_title": "Introduction",
                "content": []
            }
            sections.append(current_section)

        # For tables, you might want to mark it
        if el_type == "Table":
            current_section["content"].append({"table": el_text})
        elif el_type == "FigureCaption":
            current_section["content"].append({"figure_caption": el_text})
        else:
            current_section["content"].append(el_text)

    # Ignore PageBreaks, Footnotes, etc.

# Output cleaned JSON
print(json.dumps(sections, indent=2, ensure_ascii=False))