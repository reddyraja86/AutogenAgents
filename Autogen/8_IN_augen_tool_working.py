import os
from dotenv import load_dotenv
from typing import Annotated
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time


from autogen import ConversableAgent, AssistantAgent,UserProxyAgent

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


def extract_readable_content_from_url(url: str) -> str:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, timeout=30000)
            page.wait_for_selector("body", timeout=10000)

            # Get clean visible text
            body_text = page.inner_text("body")

            # Optionally grab meta and title
            title = page.title()
            meta_description = page.locator("meta[name='description']").get_attribute("content")

            content = f"Title: {title}\n"
            content += f"Description: {meta_description}\n\n"
            content += f"Content:\n{body_text}"

            browser.close()
            return content

        except PlaywrightTimeoutError:
            browser.close()
            return "❌ Page took too long to load."
        except Exception as e:
            browser.close()
            return f"❌ Error extracting content: {e}"






# ✅ User agent that can execute the function
agenttool = AssistantAgent(
    name="agenttool",
    system_message="You are a helpful AI agent. You can call function and return information.",
    llm_config=llm_config
    
)

agenttool.register_for_execution(name="search_google_and_get_first_link")(search_duckduckgo_and_get_first_link)



extactcontent = AssistantAgent(
    name="extactcontent",
    system_message="You are a helpful AI agent. You can extract the content from the url mentiond .",
    llm_config=llm_config
    
)

extactcontent.register_for_execution(name="extract_readable_content_from_url")(extract_readable_content_from_url)

contencreator_from_html_agent = AssistantAgent(
    name="contencreator_from_html_agent",
    system_message=" you are a content creator agent. You can can crete the content from the tile and description ,content provided. Also beaitify this content and make it more readable.Also identify the main topic of the content.If there are any products or services mentioned in the content, provide a brief description of each product or service, including its name, features, and benefits , cost .",
    llm_config=llm_config,
)

products_list_agent = AssistantAgent(
    name="products_list_agent",
    system_message=" you are a product list agent . You will list down the products and services mentioned in the content provided. Also the price of the product and services, Discounts.",
    llm_config=llm_config,
)

summarizer = AssistantAgent(
    name="Summarizer",
    system_message="You are a website summarizer. return a short summary in 3 lines about the website.",
    llm_config=llm_config
)

user_proxy = UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "").strip().lower() in ["exit", "quit"],
    max_consecutive_auto_reply=0,  # ✅ No back-and-forth
    code_execution_config=False
)


# Main chain execution
if __name__ == "__main__":
    website_name = input("Enter a your search string  name: ")
    print(f"User input: {website_name}")

    chat_results = user_proxy.initiate_chats([
        {"recipient": contencreator_from_html_agent, "message": extract_readable_content_from_url(search_duckduckgo_and_get_first_link(website_name))},
        {"recipient": products_list_agent, "message": "{{contencreator_from_html_agent.response}}"},
        {"recipient": summarizer, "message": "{{webscraper.response}}"}
    ])
    

    print("\n📋Final Chat History:")
    print(chat_results[-1].chat_history[-1]["content"] ) 
    print("\n📋 Final output from content creator contencreator_from_html_agent:")
    print(chat_results[0].chat_history[-1]["content"])
    print("\n📋 Final output from product list agent:") 
    print(chat_results[1].chat_history[-1]["content"])
    print("\n📋 Final output from summarizer:") 
    print(chat_results[2].chat_history[-1]["content"])




    


