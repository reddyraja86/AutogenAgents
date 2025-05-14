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
writer = AssistantAgent(
    name="Writer",
    system_message="You are a writing helper and assistent for me ,please write something about the mentioned topic.",
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
    sentense = input("Enter what i need to Do: ")
    print(f"User input: {sentense}")

    chat_results = user_proxy.initiate_chats([
        {"recipient": writer, "message": sentense},
    ])

    print("\nFinal output from recommender:")
    print(chat_results[0]['messages'][-1]['content'])
    print(chat_results[0].chat_history[-1]["content"])
