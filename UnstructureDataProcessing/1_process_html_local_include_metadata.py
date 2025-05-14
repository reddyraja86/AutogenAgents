from unstructured.partition.html import partition_html
import json

input_filepath = "../pdfs/el_nino.html"


pptx_elements = partition_html(filename=input_filepath)
element_dict = [el.to_dict() for el in pptx_elements]

print(json.dumps(element_dict, indent=2))
