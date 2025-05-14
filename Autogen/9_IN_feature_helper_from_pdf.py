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

# Read list of pdf files  content from a directory
def read_pdf_files_from_directory(directory_path: str) -> str:
    pdf_text = ""
    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory_path, filename)
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            for page in reader.pages:
                pdf_text += page.extract_text() + "\n\n"
    return pdf_text



# Setup AutoGen Assistant
data_analyst = AssistantAgent(
    name="DataAnalyst",
    system_message="You are a data analyst. Answer questions about pdfs data that is shared with you.",
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
    directory_path = "pdfs"  # Change to your file path
    pdf_text = read_pdf_files_from_directory(directory_path)
    print("✅ pdf files loaded. Ask me anything about it!")
    print("Type 'exit' to stop.\n")

    while True:
        question = input("❓ Your question: ")
        if question.strip().lower() in ["exit", "quit"]:
            break

        prompt = f"""Here is the PDF data:\n\n{pdf_text}\n\nQuestion: {question}"""

        # Initiate chat
        chat_result = user_proxy.initiate_chat(data_analyst, message=prompt)

        # Show last message
        print("\n🧠 Answer:")
        print(chat_result.chat_history[-1]["content"])
        print("-" * 50)
