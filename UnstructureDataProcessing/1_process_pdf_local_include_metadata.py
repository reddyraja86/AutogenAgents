from unstructured.partition.pdf import partition_pdf
import json

input_filepath = "../pdfs/OTC-DictionaryAPI.pdf"
print(f"🔵 Reading PDF file: {input_filepath}")
elements = partition_pdf(filename=input_filepath)

# Prepare output including metadata
element_dicts = []
for element in elements:
    # Safely handle coordinates
    # if element.metadata.coordinates is not None:
    #     coords = {
    #         "points": element.metadata.coordinates.points
    #     }
    # else:
    #     coords = None

    element_info = {
        "type": type(element).__name__,
        "text": element.text,
        "metadata": {
            "page_number": element.metadata.page_number,
            "filename": element.metadata.filename,
            # "coordinates": coords,
        }
    }
    element_dicts.append(element_info)
print(f"🔵 Number of elements: {len(element_dicts)}")
# Now safe to JSON serialize
json_elements = json.dumps(element_dicts, indent=2)
print(json_elements)
