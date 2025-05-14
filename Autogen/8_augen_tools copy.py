import os
from dotenv import load_dotenv
from typing import Annotated
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time


from autogen import ConversableAgent, AssistantAgent

load_dotenv()

# LLM Configuration for Ollama
llm_config = {
    "config_list": [
        {
            "model": "llama3.2",
            "base_url": "http://localhost:11434/v1",
            "api_key": "ollama",
            "price": [0, 0]
        }
    ]
}

def search_duckduckgo_and_get_first_link(query: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)  # Headless=False for visibility
        page = browser.new_page()

        try:
            print("🔍 Navigating to DuckDuckGo...")
            page.goto("https://duckduckgo.com", timeout=30000)  # Increased timeout for page load

            # Wait for the input field to appear and become visible
            print("⏳ Waiting for the search input field...")
            page.wait_for_selector("input[name='q']", timeout=10000)  # Wait for search input field

            # Type query and hit Enter
            print(f"🔎 Searching for: {query}")
            page.fill("input[name='q']", query)
            page.keyboard.press("Enter")

            # Wait for the results to load and stabilize (checking for results with data-testid)
            print("⏳ Waiting for result links with data-testid='result-title-a'...")
            page.wait_for_selector('[data-testid="result-title-a"]', timeout=30000)  # Wait for the result link

            # Extract the first result's href
            print("✅ Extracting first result link...")
            first_result = page.locator('[data-testid="result-title-a"]').first  # Locating the first result link
            href = first_result.get_attribute("href")

            browser.close()
            return href or "❌ No link found in the first result."

        except PlaywrightTimeoutError:
            browser.close()
            return "❌ Search results did not load in time."
        except Exception as e:
            browser.close()
            return f"❌ Error: {e}"

# 🔍 Try it directly
if __name__ == "__main__":
    result = search_duckduckgo_and_get_first_link("OpenText")
    print("🔗 First link:", result)



# ✅ Assistant Agent that suggests function calls
webscraper = AssistantAgent(
    name="webscraper",
    system_message="You are a helpful AI web scraper. Return 'TERMINATE' when the task is done.",
    llm_config=llm_config,
)

# ✅ Register function with LLM so it can suggest it
webscraper.register_for_llm(
    name="search_google_and_get_first_link",
    description="Search Google and get the first link"
)(search_duckduckgo_and_get_first_link)

# ✅ User agent that can execute the function
user = ConversableAgent(
    name="user",
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", ""),
    max_consecutive_auto_reply=1,  # Limit to one auto reply for this example
    
)

# ✅ Register function for execution
user.register_for_execution(name="search_google_and_get_first_link")(search_duckduckgo_and_get_first_link)

# ✅ Start the conversation
chatResult = user.initiate_chat(
    webscraper,
    message="explain about this website " + search_duckduckgo_and_get_first_link('opentext')
)

print(chatResult['messages'][-1]['content'])  # Print the final output from the assistant agent


