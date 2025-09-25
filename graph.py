from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_mistralai import ChatMistralAI
from langchain.schema import BaseMessage
import config

def add_messages(left: list[BaseMessage], right: list[BaseMessage]) -> list[BaseMessage]:
    """Add messages to the state."""
    return left + right

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

llm = ChatMistralAI(
    model=config.settings.DEFAULT_MODEL,
    api_key=config.settings.MISTRAL_API_KEY,
    temperature=config.settings.TEMPERATURE
)

def chat_node(state: ChatState):
    """Process chat messages through LLM and return response."""
    # take user query from state
    messages = state['messages']

    # send to llm
    response = llm.invoke(messages)

    # response store state
    return {'messages': [response]}

def create_chatbot():
    """Create and compile the chatbot graph."""
    # Create graph
    graph = StateGraph(ChatState)

    # Add node
    graph.add_node('chat_node', chat_node)

    # Set entry point
    graph.set_entry_point('chat_node')

    # Add edge to end
    graph.add_edge('chat_node', END)

    # Checkpointer
    checkpointer = InMemorySaver()

    # Compile and return chatbot
    return graph.compile(checkpointer=checkpointer)

# Create the chatbot instance
chatbot = create_chatbot()