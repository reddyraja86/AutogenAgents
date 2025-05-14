import os
from autogen import ConversableAgent, GroupChat, GroupChatManager
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

coordinatorAgent = ConversableAgent(
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
    # # Print the final output from the coordinator agent
    # print("\nFinal output from coordinator agent:")
    # print(chat_results[-1]['messages'][-1]['content'])
    # # Print the final output from the neutral agent
    # print("\nFinal output from neutral agent:")
    # print(chat_results[-2]['messages'][-1]['content'])
    # # Print the final output from the pro agent
    # print("\nFinal output from pro agent:")
    # print(chat_results[-3]['messages'][-1]['content'])
    # # Print the final output from the con agent
    # print("\nFinal output from con agent:")
    # print(chat_results[-4]['messages'][-1]['content'])
    

