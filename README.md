#  Setting up the development enviorment

## To create a Python project that utilizes autogen with Jupyter Lab, follow these steps:

### Step 1: Set Up Virtual Environment

1. Install Virtual Environment:

   If you haven't already, install the virtual environment package: `pip install virtualenv`

2. Create the Virtual Environment:

   Navigate to your project folder:  `cd your_project_directory`

   Create a new virtual environment:  `virtualenv myenv`

3. Activate the Virtual Environment:

   On Windows: `myenv\Scripts\activate`

   You should now see a `(.env)` at the beginning of your prompt terminal line.


### Step 2: Install Required Packages

1. Install Jupyter Lab and Autogen:

   With your virtual environment activated,

   install Jupyter Lab and Autogen: `pip install jupyterlab autogen`

### Step 3: Launch Jupyter Lab

1. Run Jupyter Lab:

   Start Jupyter Lab by running:  `jupyter lab`


#### What is LLM?

- LLM is a language model which is trained on a large dataset and can be used to generate text.
- It is a type of AI model that is trained on a large amount of text data and can be used to generate text.

####  what is Agent?

- Agent is the one which take user question and interact with multiple tools and provide this info to LLM to get the desired answer

# Autogen

- Autogen is an open source framework programming framework that allows developers to build AI agents.

-  Key Components of Autogen:
  -  Core Component - Autogen Agent: The central element in Autogen is the autogen agent, which manages message sending and receiving. This agent can utilize different LLMs, execute Python code, and integrate human feedback into its processes.
  -  Conversable Agent: This is a specific type of Autogen agent designed to enhance communication capabilities. It includes multiple components like a list of language models, a code executor, and a mechanism for integrating human feedback. The conversable agent is essentially a specialized version of the Autogen agent, tailored for interactive and conversational applications.

### Create a first autoagen app

1. Create a new folder for your project.
2. Create a virtual environment for your project.
3. Install Autogen.

 ```
 pip install virtualenv
 virtualenv myenv
 myenv\Scripts\activate
 pip install autogen
 pip install python-dotenv
 myenv\Scripts\activate
 
 ```

4. Code sample 

```python
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
            }
        ])
    print(response)
except Exception as e:
    print(f"Error: {e}")



```

 ### Agents main taks
1. Interacting with 'LLM'
2. Interacting with 'tools' to get the work done
3. Interacting with 'human inputs'
4. Interacting with other agents


### To do the above we have following in autogen

1. ##### ConversableAgent Agent: ( For everything we can use)
   - Core agent type that can send and receive messages.
   - Highly customizable:
     - Integrates with LLMs, tools, and human input.
     - Configurable settings like human_input_mode (e.g., NEVER) and code_execution_config (e.g., False).
     - Supports default system messages to define agent behavior (e.g., "You are an AI assistant specializing in X, Y, Z").
2. ##### Assistant Agent ( Inherited from ConversableAgent ):
   - Interacts with LLM.
   - Acts as an AI assistant using LLMs (e.g., GPT-3, GPT-4).
   - Capabilities:
     - Writes Python code.
     - Suggests corrections and bug fixes.
     - Customizable with system messages and LLM configurations.
3. ##### User Proxy Agent ( Inherited from ConversableAgent ):
   - Takes human inputs and responds to the user.
   - Acts on behalf of humans and interacts with them.
   - Features:
     - Requests human input for replies.
     - Can execute code found in messages (if enabled).
     - Configurable to disable code execution (code_execution_config=False).
 4. ##### Group Chat Manager ( Inherited from ConversableAgent ):
    - Orchestrates communication between multiple agents.
    - Useful when human_input_mode=NEVER to manage agent interactions without human involvement.

![Build-in Agents in Autogen](Build-in%20Agents%20in%20Autogen.jpg)



### Example application on Useragent 

- Here user agent accepts the user inputs and connects with the Assistant agent which responds by connecting with the LLM


This program sets up a multi-agent system using the `autogen` library. Here's a summary of what it does:

1. **Environment Setup**:
    - Loads environment variables using `dotenv` for sensitive information like API keys.

2. **LLM Configuration**:
    - Configures a language model (`llama3.2`) with a base URL and API key.

3. **Agent Initialization**:
    - Creates two agents:
        - `UserProxyAgent`: Acts as a proxy for the user, responding only with the information it has.
        - `AssistantAgent`: A helpful assistant agent with similar constraints.

4. **Agent Interaction**:
    - The `UserProxyAgent` initiates a chat with the `AssistantAgent`. The interaction is limited to a maximum of 2 consecutive auto-replies.

5. **Error Handling**:
    - Wraps the chat initiation in a `try-except` block to handle any exceptions gracefully.

This program demonstrates a basic setup for building and interacting with multi-agent systems.



```python
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
    code_execution_config=False
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

```

- Insome use cases Agent will generate the code and execute the same to store that code and execute we wil use the work_dir


``` python
import os
from autogen import AssistantAgent, UserProxyAgent

# Step 1: LLM Config for Ollama (running locally)

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

# Step 2: Assistant Agent powered by Ollama
assistant = AssistantAgent(
name="chart_assistant",
llm_config=llm_config
)

# Step 3: UserProxyAgent with code execution enabled
user_proxy = UserProxyAgent(
name="user",
code_execution_config={
"work_dir": "workspace",      # Folder where generated code is stored & run
"use_docker": False,           # Set True if you want sandboxing
"install_libraries": True      # Allow AutoGen to install missing packages
}
)

# Step 4: Start a task via direct interaction
user_proxy.initiate_chat(
assistant,
message="""
Plot a bar chart using matplotlib showing revenue over Q1:
January - 2000, February - 2500, March - 1800.
Display the chart using plt.show().
"""
)
```
 
### AutoGen supports 3 modes for human input:

- **NEVER** - human input is never requested
- **TERMINATE** (default) - human input is only requested when a termination condition is met
- **ALWAYS** - human input is always requested. Human skip and trigger an auto-reply.


  ```python
  # when you have NEVER mode it will not accept the input from user in console. and  llm_config will be passed to the agent.   
  llm_config=llm_config,
  human_input_mode="NEVER",

  # when you have ALWAYS mode it will accept the input from user in console. and  llm_config will not be passed to the agent.
  llm_config=False,
  human_input_mode="ALWAYS",

```

### Example on guessing numbers to understand Human input

```python
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

```


### Autogen connecting to the Tools
 - We have no control on code written by autogen using LLM so we make use of the Tools 
 - We have no control over what an agent writes (code).
   
   **Tools in AutoGen:**
   - Pre-defined functions
   - Controlled actions
   - Controlled availability

 #### Autogen tools are typically used to:
 - Extend AI Capabilities: They allow the assistant to perform specific tasks (e.g., calculations, data processing) by integrating external functions or APIs.

```python
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


```


### Conversation Patterns 

 - **Two-agent chat:** simplest conversation pattern with two agents chatting (used the initiate_chat method)
 - **Sequential** a series of two-agents linked  by a carryover mechanism
 - **Group Chat** involves more than two agents
 - **Nested Chat** combines a workflow into a single agent for reuse in larger workflows
  

#### Sequential Conversation Patterns

 - This will allow us to chain multiple agents together in a sequential manner.
 - The first agent will initiate the conversation and the second agent will respond to the first agent.
 - The first agent will carry over the context to the second agent.
 - The second agent will carry over the context to the third agent and so on.


```python
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

```


#### Group Chat

 - Multiple agents can conmmunicate as a group


```python
import os
from autogen import ConversableAgent, GroupChat, GroupChatManager,UserProxyAgent
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


# Lets build a debate agent where one agent talks about the pros and the other agent talks about the cons of a topic. and then a coordinator agent intiates the chat by gicing a topics at the end summarizes the debate and gives a final recommendation.fourth agent talks nutrally about the topic and gives a summary of the debate. 

# Define the agents
proAgent = ConversableAgent(
    name="ProAgent",
    system_message="You are an agent that discusses the pros of a given topic.",
    llm_config=llm_config,
    description="Discusses the pros of a topic.",
)   

conAgent = ConversableAgent(
    name="ConAgent",
    system_message="You are an agent that discusses the cons of a given topic.",
    llm_config=llm_config,
    description="Discusses the cons of a topic.",
)   

nutralAgent = ConversableAgent(
    name="NutralAgent",
    system_message="You are an agent that discusses the topic neutrally and summarizes the debate.",
    llm_config=llm_config,
    description="Discusses the topic neutrally and summarizes the debate.",
)   

coordinatorAgent = UserProxyAgent(
    name="CoordinatorAgent",
    system_message="You are an agent that coordinates the debate and you gives the topic by taking the input from user and at the end provides a final recommendation.",
    llm_config=llm_config,
    description="Coordinates the debate and provides a final recommendation.",
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "").strip().lower() in ["exit", "quit"],
    max_consecutive_auto_reply=1,
    code_execution_config=False
)

# Create a Group Chat
group_chat = GroupChat(
    agents=[proAgent, conAgent, nutralAgent, coordinatorAgent],
    messages=[],
    max_round=10,
)


# Create a Group Chat Manager
group_chat_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config
)




if __name__ == "__main__":
    topic_name = input("Let's have a debate about the topic of your choice: ")
    # Get user input for the topic name
    print(f"User input: {topic_name}")
    
    chat_results = group_chat_manager.initiate_chat(
        coordinatorAgent,
        message=topic_name,
        summary_method="reflection_with_llm",
    )
    
``` 

### Nested Chat

