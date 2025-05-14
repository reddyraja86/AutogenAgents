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
