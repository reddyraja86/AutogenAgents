import os
from autogen import ConversableAgent,AssistantAgent,UserProxyAgent
from typing import Annotated
from dotenv import load_dotenv

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



# Define simple calculator functions
def add_numbers(
    a: Annotated[int, "First number"], b: Annotated[int, "Second number"]
) -> str:
    return f"The sum of {a} and {b} is {a + b}."


def multiply_numbers(
    a: Annotated[int, "First number"], b: Annotated[int, "Second number"]
) -> str:
    return f"The product of {a} and {b} is {a * b}."


# Define the assistant agent that suggests tool calls.
assistant = AssistantAgent(
    name="CalculatorAssistant",
    system_message="You are a helpful AI calculator. Return 'TERMINATE' when the task is done.",
    llm_config=llm_config,
)

# The user proxy agent is used for interacting with the assistant agent and executes tool calls.
user_proxy = ConversableAgent(
    name="User",
    is_termination_msg=lambda msg: msg.get("content") is not None
    and "TERMINATE" in msg["content"],
    human_input_mode="NEVER",
)

# Register the tool signatures with the assistant agent.
assistant.register_for_llm(name="add_numbers", description="Add two numbers")(
    add_numbers
)
assistant.register_for_llm(name="multiply_numbers", description="Multiply two numbers")(
    multiply_numbers
)

# Register the tool functions with the user proxy agent.
user_proxy.register_for_execution(name="add_numbers")(add_numbers)
user_proxy.register_for_execution(name="multiply_numbers")(multiply_numbers)

user_proxy.initiate_chat(assistant, message="What is the division of 7 and 5?")

