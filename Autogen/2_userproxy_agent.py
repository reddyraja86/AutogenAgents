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

user_agent = UserProxyAgent(
    name="UserRaju",
    system_message= " You are a user proxy agent. You can only respond to the user with the information you have.",
    llm_config=llm_config,
    human_input_mode="NEVER",
    code_execution_config={
        "work_dir": "workspace",  # directory where code will run
        "use_docker": False       # optional: set True if you want isolation
    }  
)

assistant_agent = AssistantAgent(
    name="assistant-agent",
    system_message= "You are a helpful assistant agent. You can only respond to the user with the information you have.",
    llm_config=llm_config,
    human_input_mode="NEVER",
    code_execution_config=False       
)


try:
    response = user_agent.initiate_chat(recipient=assistant_agent,
        # message=   "Can you explain me about autogen?" , # If i dont pass this message , it will accept the message from user in console
        function_map=None,  # No functions to map
        max_consecutive_auto_reply=2 # Limit to 1 auto reply      
    )                 
    print(response)
except Exception as e:
    print(f"Error: {e}")


