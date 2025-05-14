import sys
import io
import pandas as pd
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent
from unstructured.partition.pdf import partition_pdf
import json,logging,autogen
from autogen import runtime_logging
import sys
from rich.console import Console
from rich.markdown import Markdown
import io
import time
import threading
from tqdm import tqdm
import time
import asyncio
from asyncio import constants
from playwright.async_api import async_playwright
from openpyxl import Workbook
from markdown import markdown
from IPython.core.display import display, HTML
from bs4 import BeautifulSoup

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

async def  read_browser_and_create_xls_file():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context()
        page = await context.new_page()
        context.clear_cookies()

        # Get screen dimensions
        # screen_width = page.evaluate("window.screen.width")
        # screen_height = page.evaluate("window.screen.height")
        # Set viewport size to screen dimensions
        # page.set_viewport_size({"width": 1920, "height": 1080})

        # Grant clipboard permissions in ValueEdge for the target origin to avoid the popup in the browser
        await context.grant_permissions(
            ["clipboard-read", "clipboard-write"],
            origin="https://ot-internal.saas.microfocus.com"
        )

        # Navigate to the login page
        await page.goto('https://ot-internal.saas.microfocus.com/ui/entity-navigation?p=4001/13001&entityType=work_item&id=3366321')

        page.set_default_timeout(12000)

        # Fill in the login form
        await page.click('input[name="federateLoginName"]')
        await page.type('input[name="federateLoginName"]', 'hsinha@opentext.com') # type: ignore

        #Continue button
        await page.click('button[class="button--primary"]')
        page.set_default_timeout(15000)

        #if login screen appears
        # await page.fill('input[name="username"]', 'hsinha')
        # await page.fill('input[name="password"]', 'Bharat@831750')
        # await page.click('button[id="submit_button"]')

        #main login
        await page.fill('input[id="username"]', 'hsinha')
        await page.fill('input[id="password"]', 'Bharat@831750')
        await page.click('input[name="submit"]')

        page.set_default_timeout(12000)

        # Wait for the push notification approval
        print("Please approve the push notification on your mobile device.")
        await page.click('button[name="loginButton2"]')
        await page.wait_for_timeout(25000)  # Adjust the timeout as needed
        print("approved in the mobile devices and timeout ended")

        #ValueEdge ID
        await page.wait_for_timeout(8000)
        ValueEdge_id = await page.click('button[data-action-name="copyLinkAction"]')
        ValueEdge_id = await page.evaluate("navigator.clipboard.readText()")
        print("ValueEdge ID:",ValueEdge_id)

        #Product details
        Product = page.locator('div[aria-label="Product (PHT)"]')
        Product_name = await Product.inner_text()
        print("Product :",Product_name)

        #Defects Title
        # Locate and extract defects text from the specified element
        Defects_Title = page.locator('div[class="flex--1 entity-form-document-view-header-name-field-container"]')
        Title = await Defects_Title.inner_text()
        print("Title:", Title)

        #Description
        Description = page.locator('div[aria-label="Description textbox"]')
        Defects_description = await Description.inner_text()
        print("Description:",Defects_description)

        #Comments
        await page.click('button[aria-label="Comments"]')
        Comment = page.locator('div[class="absolute-stretch overflow--auto alm-entity-form-comment-lines comments-container"]')
        Comments = await Comment.inner_text()
        print("Comments :",Comments)

        #Issue Type
        Issue = page.locator('div[aria-label="Issue Type"]')
        Issue_type = await Issue.inner_text()
        print("Issue type :",Issue_type)

        #defects status
        status = page.locator('span[data-aid="entity-life-cycle-widget-current-phase-label phase.defect.closed"]')
        Defects_Status = await status.inner_text()
        print("Status:",Defects_Status)

        await page.wait_for_timeout(3000)  # Brief pause to ensure clipboard has the text

        # --- Generate Excel Report ---
        # Create a new workbook and select the default worksheet
        wb = Workbook()
        ws = wb.active
        ws.title = "Defects Report"

        # Write headers in separate columns (Column A: Title, Column B: Summary, Column C : Team)
        ws.append(["Product", "Title", "Description", "Comments", "Issue Type", "ValueEdge ID", "Status"])

        # Write the defects title and summary as a new row in the worksheet
        ws.append([Product_name, Title, Defects_description, Comments, Issue_type, ValueEdge_id, Defects_Status])

        # Save the workbook to a file
        report_filename = "defects_report123.xlsx"
        wb.save(report_filename)
        print(f"Excel report generated: {report_filename}")

        # Close the browser
        await browser.close()

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
    print("🔵 Generating summaries for each row...")
    for row in data:
        summary = generate_summary(row)  # Generate a summary for the current row
        row['Summary'] = summary  # Add summary as a new attribute
    
    # Convert the updated data back to a JSON string with indentation for readability
    updated_json_string = json.dumps(data, indent=2)
    
    # Output the updated JSON string
    #print(f"✅ Updated JSON with summaries: {updated_json_string}")
    
    return updated_json_string

def generate_summary(row_dict):
    """Generate a short summary for a single row."""
    prompt = f"Summarize the following work item information which contains details like product,title,Description,Comments,IssueType and if this is support request type or bug or CPE Incident then generate the Solution along with summary :\n{json.dumps(row_dict, indent=2)}"
    
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
    #print(f"🔵 Summary for row: {summary}")
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
data_analyst = AssistantAgent(
    name="DataAnalyst",
    system_message="You are a data analyst. Answer questions about Excel data that is shared with you.",
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
    # asyncio.run(read_browser_and_create_xls_file())
    excel_path = "defects_report123.xlsx"  # Change to your file path
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
        # print(chat_result.chat_history[-1]["content"])
        response_md = chat_result.chat_history[-1]["content"]

# Create rich console instance
        console = Console()

# Render markdown in terminal beautifully
        console.print(Markdown(response_md))
        # # Get the markdown response from the last chat message
        # response_md = chat_result.chat_history[-1]["content"]
        # # Convert markdown to HTML
        # response_html = markdown(response_md)
        # # Convert HTML to plain text (strips markdown formatting)
        # plain_text = BeautifulSoup(response_html, features="html.parser").get_text()
        # # Print clean plain text to the console
        # print(plain_text)
        print("-" * 50)
