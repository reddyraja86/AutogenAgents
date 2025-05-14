import os
import pandas as pd
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent
from unstructured.partition.xlsx import partition_xlsx
import json

load_dotenv()

# LLM configuration for local Ollama or another backend
llm_config = {
    "config_list": [
        {
            "model": "llama3.2",
            "base_url": "http://localhost:11434/v1",
            "api_key": "ollama",
            "price": [0, 0],
        }
    ]
}


# Setup AutoGen Assistant
data_analyst = AssistantAgent(
    name="DataAnalyst",
    system_message="You are a data analyst. Answer questions about Excel data that is shared with you.",
    llm_config=llm_config,
    # i want to remember the context of the conversation and not forget the previous messages.
    
)

# User agent
user_proxy = UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "").strip().lower() in ["exit", "quit"],
    max_consecutive_auto_reply=0,  # ✅ No back-and-forth
    code_execution_config=False,
    
    # Set to True if you want to allow code execution
)

if __name__ == "__main__":
    input_filepath = "data.xlsx"
    elements = partition_xlsx(filename=input_filepath)

    table_data = []
    for element in elements:
        # Debugging: Print the type and attributes of each element
        print(f"Processing element of type: {type(element).__name__}")
        print(f"Element attributes: {dir(element)}")
        
        # Check if the element is a table
        if hasattr(element, 'table') and element.table is not None:
            # Process table rows into objects
            headers = element.table[0] if len(element.table) > 0 else []  # Ensure headers exist
            for row in element.table[1:]:  # Skip the header row
                if len(row) == len(headers):  # Ensure row matches header length
                    obj = {headers[i]: row[i] for i in range(len(headers))}
                    table_data.append(obj)
                else:
                    print(f"Row length mismatch: {row}")
        else:
            print("Non-table element found or table is empty:")
            print(f"Element text: {getattr(element, 'text', 'N/A')}")
            print(f"Element metadata: {getattr(element, 'metadata', 'N/A')}")

    if table_data:
        print("Extracted table data as list of objects:")
        print(table_data)
    else:
        print("No table data was extracted. Please check the input file and ensure it contains valid tables.")

    # Prepare output including metadata
    element_dicts = []
    for element in elements:

        element_info = {
            "type": type(element).__name__,
            "text": element.text,
            "metadata": {
                "page_number": element.metadata.page_number,
                "filename": element.metadata.filename,
            }
        }
        element_dicts.append(element_info)

    # Now safe to JSON serialize
    json_elements = json.dumps(element_dicts, indent=2)
    #print(json_elements)
    excel_text = json_elements
    print("✅ Excel file loaded. Ask me anything about it!")
    print("Type 'exit' to stop.\n")
    # print(excel_text)  # Print the content of the Excel file
    while True:
        question = input("❓ Your question: ")
        if question.strip().lower() in ["exit", "quit"]:
            break

        prompt = f"""Here is the Excel data:\n\n{excel_text}\n\nQuestion: {question}"""

        # Initiate chat
        chat_result = user_proxy.initiate_chat(data_analyst, message=prompt)

        # Show last message
        print("\n🧠 Answer:")
        print(chat_result.chat_history[-1]["content"])
        print("-" * 50)
