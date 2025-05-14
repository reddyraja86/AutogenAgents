from unstructured.partition.pdf import partition_pdf
import json
import logging

logging.basicConfig(level=logging.INFO)

input_filepath = "../pdfs/fake-memo.pdf"

# Use the local partitioner
elements = partition_pdf(filename=input_filepath)
print(f"Number of elements: {len(elements)}")

# Prepare output as JSON
element_dicts = [
    {
        "type": type(element).__name__, 
        "text": element.text
    } 
        for element in elements
    ]
print(f"Number of elements in JSON: {len(element_dicts)}")
# Convert to JSON string with indentation for readability
json_elements = json.dumps(element_dicts, indent=2)

# Print the processed data
print(json_elements)
