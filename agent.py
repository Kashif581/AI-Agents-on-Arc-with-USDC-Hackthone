from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os, re
from typing import TypedDict, List, Any
from langchain_core.messages import HumanMessage, AIMessage

# --- Load environment ---
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# --- Import Tools ---
from wallet_tools import (
    tool_create_wallet_set,
    tool_create_wallets,
    tool_list_wallets,
    tool_get_wallet_balance,
    tool_transfer_token,
)

# --- Define State ---
class WalletState(TypedDict):
    messages: List[Any]

# --- Memory (short-term session context) ---
session_memory = {
    "wallet_set_name": None,
    "wallets": {},  # e.g., {"User": "0x123...", "Electricity": "0x456..."}
}

# --- Helper: Update memory from model replies ---
def update_session_memory(agent_response: str):
    # Extract wallet set name
    match = re.search(r"wallet set name[:\s]+(\w+)", agent_response, re.IGNORECASE)
    if match:
        session_memory["wallet_set_name"] = match.group(1)

    # Extract wallet name and address (if mentioned)
    wallet_match = re.findall(r"wallet\s+(\w+)\s*address[:\s]+(0x[a-fA-F0-9]+)", agent_response)
    for name, address in wallet_match:
        session_memory["wallets"][name] = address

# --- LLM + Tools Setup ---
tools = [
    tool_create_wallet_set,
    tool_create_wallets,
    tool_list_wallets,
    tool_get_wallet_balance,
    tool_transfer_token,
]

llm = ChatGroq(model="llama-3.1-8b-instant", api_key=groq_api_key)
llm_with_tools = create_react_agent(llm, tools)

# --- System Prompt ---
SYSTEM_PROMPT = """You are a helpful and conversational assistant for Circle wallet management.
Before using any tool, make sure you understand what the user wants.
If details are missing (like wallet set name, number of wallets, or wallet names), ask follow-up questions.
Keep the tone natural and conversational while helping the user perform wallet actions.
"""

# --- Agent Node ---
def agent_node(state: WalletState):
    # Build memory context for this turn
    memory_context = ""
    if session_memory["wallet_set_name"]:
        memory_context += f"Current wallet set name: {session_memory['wallet_set_name']}\n"
    if session_memory["wallets"]:
        memory_context += "Known wallets:\n"
        for name, address in session_memory["wallets"].items():
            memory_context += f"  - {name}: {address}\n"

    # Add system + memory context before user messages
    memory_prompt = f"{SYSTEM_PROMPT}\nHere is the current memory context:\n{memory_context}\n"
    messages = [AIMessage(content=memory_prompt)] + state["messages"]

    if not messages:
        return {"messages": [AIMessage(content="Hi! How can I help with your wallet today?")]}

    result = llm_with_tools.invoke({"messages": messages})
    return {"messages": state["messages"] + [result]}

# --- Build Graph ---
graph = StateGraph(WalletState)
graph.add_node("agent", agent_node)
graph.add_edge("agent", END)
graph.set_entry_point("agent")
workflow = graph.compile()


def chat_with_agent(user_input: str, conversation_history: list):
    """Process user input and return the agent's reply."""
    conversation_history.append(HumanMessage(content=user_input))
    state = {"messages": conversation_history}

    result = workflow.invoke(state)
    messages = result.get("messages", [])

    if not messages:
        return "(no response from agent)"

    last_message = messages[-1]
    if isinstance(last_message, AIMessage):
        update_session_memory(last_message.content)
        conversation_history.append(last_message)
        return last_message.content
    else:
        return str(last_message)


# # --- Run Chat Loop ---
# print("Wallet Agent Ready! Type 'exit' to quit.")
# conversation_history = []

# while True:
#     user_input = input("You: ")
#     if user_input.lower() in ["exit", "quit"]:
#         break

#     # Add user message to conversation
#     conversation_history.append(HumanMessage(content=user_input))
#     state = {"messages": conversation_history}

#     # Run agent
#     result = workflow.invoke(state)
#     messages = result.get("messages", [])

#     if not messages:
#         print("Agent: (no message returned — check node logic)")
#         continue

#     # Print agent reply
#     last_message = messages[-1]
#     if isinstance(last_message, AIMessage):
#         print("Agent:", last_message.content)
#         conversation_history.append(last_message)
#         update_session_memory(last_message.content)  # update memory each turn
#     else:
#         print("Agent:", last_message)
