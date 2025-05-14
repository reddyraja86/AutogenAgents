import os
from autogen import UserProxyAgent, AssistantAgent
from dotenv import load_dotenv 

# Load environment variables
load_dotenv()

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

# Define agents
summarizer = AssistantAgent(
    name="Summarizer",
    system_message="You are a book summarizer. When given a book name, return a short summary in 3 lines.",
    llm_config=llm_config
)

sentiment_analyzer = AssistantAgent(
    name="SentimentAnalyzer",
    system_message="You are a sentiment analyzer. Given a book summary, determine the tone (positive, neutral, negative) and explain briefly.",
    llm_config=llm_config
)

recommender = AssistantAgent(
    name="Recommender",
    system_message="You are a recommender. Based on the sentiment analysis, decide if the book is worth reading and explain your answer.",
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
    book_name = input("Enter a book name: ")
    print(f"User input: {book_name}")

    chat_results = user_proxy.initiate_chats([
        {"recipient": summarizer, "message": book_name},
        {"recipient": sentiment_analyzer, "message": "{{Summarizer.response}}"},
        {"recipient": recommender, "message": "{{SentimentAnalyzer.response}}"}
    ])

    print("\nFinal output from recommender:")
    print(chat_results[-1]['messages'][-1]['content'])
