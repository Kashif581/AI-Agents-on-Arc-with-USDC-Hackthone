from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, create_react_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from typing import TypedDict, List, Any
from langchain_core.messages import HumanMessage, AIMessage

# --- Load environment ---
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# --- Import Tools ---
from wallet_tools import (
    tool_generate_secret,
    tool_generate_ciphertext,
    tool_create_wallet_set,
    tool_create_wallets,
    tool_list_wallets,
    tool_get_wallet_balance,
    tool_transfer_token,
)

# --- Define State ---
class WalletState(TypedDict):
    messages: List[Any]

# --- LLM + Tools Setup ---
tools = [
    tool_generate_secret,
    tool_generate_ciphertext,
    tool_create_wallet_set,
    tool_create_wallets,
    tool_list_wallets,
    tool_get_wallet_balance,
    tool_transfer_token,
]

# Base LLM
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=groq_api_key)

# Combine LLM with tools using a prebuilt React-style agent
llm_with_tools = create_react_agent(llm, tools)

# --- Agent Node ---
def agent_node(state: WalletState):
    """LLM agent node — decides when to call tools."""
    messages = state.get("messages", [])
    if not messages:
        return {"messages": [AIMessage(content="Hi! How can I help with your wallet today?")]}
    result = llm_with_tools.invoke({"messages": messages})
    return {"messages": messages + [result]}

# --- Build Graph ---
graph = StateGraph(WalletState)
graph.add_node("agent", agent_node)
graph.add_edge("agent", END)
graph.set_entry_point("agent")

workflow = graph.compile()

# --- Run Loop ---
print("Wallet Agent Ready! Type 'exit' to quit.")
while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        break

    state = {"messages": [HumanMessage(content=user_input)]}
    result = workflow.invoke(state)
    messages = result.get("messages", [])

    if not messages:
        print("Agent: (no message returned — check node logic)")
        continue

    last_message = messages[-1]
    if isinstance(last_message, AIMessage):
        print("Agent:", last_message.content)
    else:
        print("Agent:", last_message)
