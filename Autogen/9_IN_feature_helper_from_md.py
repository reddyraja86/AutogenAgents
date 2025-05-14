import os
import pandas as pd
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent

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

# Function to read content from a md file
def read_md_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

# Setup AutoGen Assistant
data_analyst = AssistantAgent(
    name="DataAnalyst",
    system_message="You are a data analyst. Answer questions about md file data that is shared with you. identify the Issue Description, Root Cause, Resolution, Debugging Guide , Conclusion to answer the question.",
    llm_config=llm_config,
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
    excel_path = "srequests.md"  # Change to your file path
    excel_text = read_md_file(excel_path)
    print("✅ Excel file loaded. Ask me anything about it!")
    print("Type 'exit' to stop.\n")

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
