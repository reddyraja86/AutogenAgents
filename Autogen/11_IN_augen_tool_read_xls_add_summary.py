import sys
import io
import pandas as pd
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent
from unstructured.partition.pdf import partition_pdf
import json,logging,autogen
from autogen import runtime_logging
import sys
import io
import time
import threading
from tqdm import tqdm
import time

# Set up logging (only for errors or important logs)


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
    # print("✅ Extracted Table Data:")
    # print(table_data)
    # print("\n✅ JSON Output:")
    # print(table_data_json)
    return table_data_json

def update_json_with_summary(json_string: str) -> str:
    """Accept JSON as a string, add summaries to each record, and return the updated string."""
    
    # Load the existing JSON string into a Python object (list of dictionaries)
    data = json.loads(json_string)
    
    # For each row, generate the summary and add it as a new attribute
    # print("🔵 Generating summaries for each row...")
    for row in data:
        summary = generate_summary(row)  # Generate a summary for the current row
        row['Summary'] = summary  # Add summary as a new attribute
    
    # Convert the updated data back to a JSON string with indentation for readability
    updated_json_string = json.dumps(data, indent=2)
    
    # Output the updated JSON string
    print(f"✅ Updated JSON with summaries: {updated_json_string}")
    
    return updated_json_string

def generate_summary(row_dict):
    """Generate a short summary for a single row."""
    prompt = f"Summarize the following topic based on the information:\n{json.dumps(row_dict, indent=2)}"
    
    summaryagent = AssistantAgent(
    name="summarizer",
    system_message=prompt,
    llm_config=llm_config,
    )
    
    response = summaryagent.generate_reply(
        messages=  [  
            {
                "role": "user",
                "content": prompt
            }
    ])
    
    # Extract the summary from the response
    
    summary = response
    print(f"🔵 Summary for row: {summary}")
    return summary

def read_pdf_to_json(input_filepath: str) -> str:
    """Read PDF file and convert to JSON."""
    elements = partition_pdf(filename=input_filepath)
    
    # Prepare output including metadata
    element_dicts = []
    for element in elements:
        element_info = {
            "type": type(element).__name__,
            "text": element.text,
            "metadata": {
                "page_number": element.metadata.page_number,
        #    "filename": element.metadata.filename,
            }
        }
        element_dicts.append(element_info)
    
    # Now safe to JSON serialize
    json_elements = json.dumps(element_dicts, indent=2)
    return json_elements

def combine_json_strings(json_string1: str, json_string2: str) -> str:
    """Combines two JSON strings representing lists of objects into a single JSON string."""
    
    # Parse both JSON strings into Python lists
    list1 = json.loads(json_string1)
    list2 = json.loads(json_string2)
    
    # Ensure both are lists
    if not isinstance(list1, list) or not isinstance(list2, list):
        raise ValueError("Both JSON inputs must represent lists.")
    
    # Combine the two lists
    combined_list = list1 + list2
    
    # Convert back to a JSON string
    combined_json_string = json.dumps(combined_list, indent=2)
    
    return combined_json_string

def show_loading(stop_event):
    while not stop_event.is_set():
        for dot_count in range(4):
            print("\r🤖 Thinking" + "." * dot_count + "   ", end="", flush=True)
            time.sleep(0.5)
            
def show_spinner(stop_event):
    with tqdm(total=0, bar_format="🤖 Thinking... {postfix}", postfix="") as pbar:
        while not stop_event.is_set():
            pbar.set_postfix_str("." * ((int(time.time() * 2)) % 4))
            time.sleep(0.5)

# Function to suppress AutoGen output and run chat
def silent_chat_with_loading(user_proxy, assistant, prompt):
    stop_event = threading.Event()
    loader_thread = threading.Thread(target=show_spinner, args=(stop_event,))
    
    # Start loader
    loader_thread.start()

    # Suppress AutoGen output
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        result = user_proxy.initiate_chat(assistant, message=prompt)
    finally:
        stop_event.set()         # stop loading
        loader_thread.join()
        sys.stdout = original_stdout
    return result

# Setup AutoGen Assistant
# data_analyst = AssistantAgent(
#     name="DataAnalyst",
#     system_message="""You are a helpful data analyst. Given structured JSON data from an Excel sheet with fields like 'Story points', 'Developer', 'Sprint', and 'Description', respond to user questions by analyzing the relevant records. Always refer to specific values from the data.""",
#     llm_config=llm_config,
# )
data_analyst = AssistantAgent(
    name="DataAnalyst",
    system_message="""
You are a helpful and intelligent data analyst.

You are provided with structured JSON data derived from an Excel file. The data contains fields such as:
- 'VE ID': Unique identifier for a feature or task
- 'Developer': The person responsible for the task
- 'Topics': Subject areas related to the task
- 'Story points': Effort estimation
- 'Sprint': Sprint number or name
- 'Story Type': Type of the story (bug, feature, etc.)
- 'Team': Indicates Team working on the task
- 'Planning Interval': Planning period or sprint
- 'Version': Release version
- 'Acceptance Criteria': Additional details

When answering user questions:
- Understand natural variations (e.g., "person" = "Developer", "effort" = "Story points", etc.)
- Provide summaries, counts, and insights based on the structured data
- Be flexible in mapping generic terms to specific columns
- If the question is ambiguous, answer with your best guess based on the field names

Always respond using clear language, and include references to exact values from the data when possible.
""",
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
    excel_path = "manager.xlsx"  # Change to your file path
    #excel_text = read_excel_to_text(excel_path)
    structured_data = read_excel_to_json(excel_path)
    structured_data_with_summary = update_json_with_summary(structured_data)
    input_filepath = "pdfs/OTC-DictionaryAPI.pdf"

    unstructured_data_from_pdf = read_pdf_to_json(input_filepath)
    
    # Combine JSON strings 
    # combined_json = combine_json_strings(excel_text_wiht_summary_from_agent, json_elements)
    
    print("✅ Data loaded. Ask me anything about it!")
    print("Type 'exit' to stop.\n")
    #print(structured_data_with_summary)  # Print the content of the Excel file
    while True:
        question = input("❓ Your question: ")
        if question.strip().lower() in ["exit", "quit"]:
            break
        # prompt =  system_message=f"""You are a data analyst.You have access to two datasets.Structured data (from XLS):{structured_data_with_summary} 
        # Unstructured data (from PDF):{unstructured_data_from_pdf}Answer user queries based on these datasets.Summarize if necessary."""
        prompt = f"""Here is the Excel data in JSON format:\n\n{structured_data_with_summary}\n\nQuestion: {question}"""
        # prompt += "\n\nPlease provide a detailed answer."
        print("\n🔵 Prompt sent to Data Analyst:")
        

        # Run silent chat
        chat_result = silent_chat_with_loading(user_proxy, data_analyst, prompt)

        # Initiate chat
        #chat_result = user_proxy.initiate_chat(data_analyst, message=prompt)
        
        # Show last message
        print("\n🧠 Answer:")
        print(chat_result.chat_history[-1]["content"])
        print("-" * 50)
