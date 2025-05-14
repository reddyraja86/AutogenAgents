from unstructured.partition.xlsx import partition_xlsx
import json

input_filepath = "../data.xlsx"

elements = partition_xlsx(filename=input_filepath)

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

# Now safe to JSON serialize
json_elements = json.dumps(element_dicts, indent=2)
print(json_elements)
