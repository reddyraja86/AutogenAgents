import os
from autogen import ConversableAgent
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

agent = ConversableAgent(
    name="simple-agent",
    llm_config=llm_config,
    human_input_mode="NEVER",
    code_execution_config=False       
)


try:
    response = agent.generate_reply(
        messages=  [  
            {
                "role": "user",
                "content": "What is the capital of France?"
            #    "content": "open google.com and serch for india and return the fierst link url?"
            }
        ])
    print(response)
except Exception as e:
    print(f"Error: {e}")


