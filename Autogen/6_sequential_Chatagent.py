import os
from autogen import UserProxyAgent,AssistantAgent
from dotenv import load_dotenv 

# Load environment variables from .env file
# This is useful if you have sensitive information like API keys
load_dotenv()

llm_config = {
    "config_list": [
        {
            "model": "llama3.2",
            "base_url": "http://localhost:11434/v1",
            "api_key": "ollama",
            "price": [0, 0]  # Suppress pricing warnings by setting prompt and completion prices to 0
        }
    ]
}


user_input_agent = UserProxyAgent(
    name="user",
    system_message= " You are a user agent. you need to ask the for the user input.",
    code_execution_config = False,
    human_input_mode="NEVER",
    llm_config=False,
    max_consecutive_auto_reply=0,  # ✅ No back-and-forth
)


# user_input_agent = UserProxyAgent(
#     name="UserRaju",
#     system_message= " You are a user agent. you need to ask the for the user input and return the result.",
#     llm_config=llm_config,
#     human_input_mode="NEVER",
#     code_execution_config={
#         "work_dir": "workspace",  # directory where code will run
#         "use_docker": False ,
#         "install_libraries": True # optional: set True if you want isolation
#     }  
# )


capital_letter_agent = AssistantAgent(
    name="Capital-Assistant",
    system_message="you are a helpful assistant agent. you will convert the user input to capital letters.",
    is_termination_msg= lambda msg: "exit" in msg["content"],   # Terminate if user says "exit",
    llm_config=llm_config,
    human_input_mode="NEVER"
)


word_count_agent = AssistantAgent(
    name="WordCount_Agent",
    system_message="You count the number of words in the text I give you.",
    llm_config=llm_config,
    human_input_mode="NEVER",
)


# The Reverse Text Agent reverses the text.
reverse_text_agent = AssistantAgent(
    name="ReverseText_Agent",
    system_message="You reverse the text I give you.",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

# The Summarize Agent summarizes the text.
summarize_agent = AssistantAgent(
    name="Summarize_Agent",
    system_message="You summarize the text I give you.",
    llm_config=llm_config,
    human_input_mode="NEVER",
)


if __name__ == "__main__":
    text = input("Enter a book name: ")
    print(f"User input: {text}")

chat_results = user_input_agent.initiate_chats(
    [
        {"recipient": capital_letter_agent, "message": text},
        {"recipient": word_count_agent, "message": "{{Capital-Assistant.response}}"},
        {"recipient": reverse_text_agent, "message": "{{WordCount_Agent.response}}"},
        {"recipient": summarize_agent, "message": "{{ReverseText_Agent.response}}"}
    ]
)

print("\nFinal output from recommender:")
print(chat_results[-1]['messages'][-1]['content'])
