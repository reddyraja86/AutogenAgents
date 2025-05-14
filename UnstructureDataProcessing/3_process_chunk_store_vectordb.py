# This script demonstrated how to read unstructured data from a PDF file,
# process it, and store the results in a Chroma vector database and perform a hybrid search.
# The script uses the Unstructured library to partition the PDF into elements,
# It also includes error handling and metadata management.

from unstructured.partition.pdf import partition_pdf
from unstructured.staging.base import dict_to_elements
from unstructured.chunking.title import chunk_by_title


import json
import chromadb

input_filepath = "../pdfs/mindset.pdf"

elements = partition_pdf(filename=input_filepath)

# Prepare output including metadata
element_dicts = []
# Convert to dicts
element_dicts = [el.to_dict() for el in elements]

# Print as JSON
print(f"Processed file: {input_filepath}")
print(json.dumps(element_dicts, indent=2))


# filter the elements based on the type of element
try:
        chapters = [
            "Embracing a Growth Mindset",
            "Strategies for Cultivating a Growth Mindset",
            "I N T R O D U C T I O N",
            "M I N D S E T",
            "T H E D R I V E R",
            "Growth vs. Fixed Mindset F I X E D",
            "F I X E D",
            "Activities",
        ]
        
        chapter_ids = {}
        for element in elements:
            for chapter in chapters:
                if element.text == chapter and element.category == "Title":
                    chapter_ids[element.id] = chapter
                    break

        print("==== chapters IDs: \n")
        print(chapter_ids)

        print("==== Elements with parent ID>>>: \n")
        chapter_to_id = {v: k for k, v in chapter_ids.items()}

        res = [
            x
            for x in elements
            if x.metadata.parent_id == chapter_to_id["Embracing a Growth Mindset"]
        ]

        # elements are objects, so you need to convert to dicts before dumping to JSON
        print(json.dumps([el.to_dict() for el in res], indent=2))

    
        # Add elements to the Chroma collection
        # Initialize Chroma DB
        chroma_client = chromadb.PersistentClient(
            path="chroma_tmp", settings=chromadb.Settings(allow_reset=False)
        )

        # Check if the collection already exists and is populated
        collection_name = "mindset"
        collection = chroma_client.get_or_create_collection(
            name=collection_name, metadata={"hnsw:space": "cosine"}
        )

        if collection.count() > 0:
            print(f"Collection '{collection_name}' already exists and is populated.")
        else:
            print(f"Collection '{collection_name}' does not exist or is empty.")
            for element in elements:
                parent_id = element.metadata.parent_id
                chapter = chapter_ids.get(parent_id, "")
                collection.add(
                    documents=[element.text],
                    ids=element._element_id,
                    metadatas=[{"chapter": chapter}],
                )
            print("Documents have been added to the Chroma collection.") 
except Exception as e:
    print(f"Error: {e}")


elements = dict_to_elements(element_dicts)  

# Chunking content
print("Chunking content...")
elements = dict_to_elements(element_dicts)
chunks = chunk_by_title(
    elements, combine_text_under_n_chars=100, max_characters=300
)
print("==== Chunks: \n")
# print(chunks)
re = json.dumps(chunks[0].to_dict(), indent=2)
print(re)

print("elements:", len(elements))
print("chunks:", len(chunks))

# Perform a hybrid search with metadata
result = collection.query(
    query_texts=["A growth mindset believes in what?"],
    n_results=2,
    where={"chapter": "Embracing a Growth Mindset"},
)
print("\n==== Query Results ==== \n")
print(json.dumps(result, indent=2))
