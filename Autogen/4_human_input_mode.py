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

random_number_generator_agent = ConversableAgent(
    name="random-number-generator-agent",
    system_message= " You are random number generator agent generates numbers between 1 to 10. You can only respond to the user with the information you have. and exit the program when user says exit or guess the correnct  number that you have generated.",
    is_termination_msg= lambda msg: "exit" in msg["content"],   # Terminate if user says "exit"
    llm_config=llm_config,
    human_input_mode="NEVER",
    code_execution_config=False       
)

guess_number_generator_agent = ConversableAgent(
    name="guess-number-generator-agent",
    system_message= " You are guess number generator agent. You will guess the numbers between 1 to 10",
    is_termination_msg= lambda msg: "6" in msg["content"],   # Terminate if user says "6"

    # when you have NEVER mode it will not accept the input from user in console. and  llm_config will be passed to the agent.
    # llm_config=llm_config,
    # human_input_mode="NEVER",
    
    # when you have ALWAYS mode it will accept the input from user in console. and  llm_config will not be passed to the agent.
    llm_config=False,
    human_input_mode="ALWAYS",
    
    code_execution_config=False       
)




try:
    response = guess_number_generator_agent.initiate_chat(
        recipient=random_number_generator_agent,
        message= "My name is Raju. I am a user. I will guess the number 3") # when you have ALWAYS mode it will accept the input from user in console. and  llm_config will not be passed to the agent.
        # message= "First I will guess the number between 1 to 10.Then you Generate a random number between 1 to 10 and tell me the number.") # when you have NEVER mode it will not accept the input from user in console. and  llm_config will be passed to the agent.
    print(response)
except Exception as e:
    print(f"Error: {e}")


