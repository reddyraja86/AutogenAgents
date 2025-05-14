from unstructured.partition.pptx import partition_pptx
import json

input_filepath = "../pdfs/msft_openai.pptx"

elements = partition_pptx(filename=input_filepath)

pptx_elements = partition_pptx(filename=input_filepath)
element_dict = [el.to_dict() for el in pptx_elements]

print(json.dumps(element_dict, indent=2))
