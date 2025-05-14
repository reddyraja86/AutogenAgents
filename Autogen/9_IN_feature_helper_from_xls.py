import os
import pandas as pd
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent
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

# Function to read Excel file and convert to string
def read_excel_to_text(file_path: str) -> str:
    df = pd.read_excel(file_path)
    return df.to_string(index=False)

def read_excel_to_json(input_filepath: str) -> str:
    # Read without specifying a header
    df = pd.read_excel(input_filepath, header=None)
    # Drop completely empty rows
    df = df.dropna(how='all')
    # Find first row that looks like headers (non-NaN values)
    header_row_index = df.first_valid_index()
    # Set that row as header
    df.columns = df.iloc[header_row_index]
    df = df.drop(index=header_row_index)
    # Drop completely empty columns (optional, to clean)
    df = df.dropna(axis=1, how='all')
    # Reset index (optional for clean dataframe)
    df = df.reset_index(drop=True)
    # Now convert to list of dicts
    table_data = df.to_dict(orient="records")
    # JSON output
    table_data_json = json.dumps(table_data, indent=2)
    # Output
    print("✅ Extracted Table Data:")
    print(table_data)
    print("\n✅ JSON Output:")
    print(table_data_json)
    return table_data_json

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
    excel_path = "mamager.xlsx"  # Change to your file path
    #excel_text = read_excel_to_text(excel_path)
    excel_text = read_excel_to_json(excel_path)
    print("✅ Excel file loaded. Ask me anything about it!")
    print("Type 'exit' to stop.\n")
    print(excel_text)  # Print the content of the Excel file
    while True:
        question = input("❓ Your question: ")
        if question.strip().lower() in ["exit", "quit"]:
            break

        prompt = f"""Here is the Excel data in JSON format:\n\n{excel_text}\n\nQuestion: {question}"""

        # Initiate chat
        chat_result = user_proxy.initiate_chat(data_analyst, message=prompt)

        # Show last message
        print("\n🧠 Answer:")
        print(chat_result.chat_history[-1]["content"])
        print("-" * 50)
