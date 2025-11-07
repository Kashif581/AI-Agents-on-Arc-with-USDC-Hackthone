import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage
from wallet_tools import (
    tool_create_wallet_set,
    tool_create_wallets,
    tool_list_wallets,
    tool_transfer_token,
    tool_get_wallet_balance
)


# --- Initialize LLM ---
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    google_api_key="AIzaSyC9byMTit8Aaf7-QvocH9SWj1eVxRN8pjE"
)



TOOLS = [
    tool_create_wallet_set,
    tool_create_wallets,
    tool_list_wallets,
    tool_transfer_token,
    tool_get_wallet_balance
]



# --- Custom System Prompt ---
SYSTEM_PROMPT = """
You are NexaPay — a friendly, helpful assistant for managing wallets using Circle's Arc developer platform.

1) Greet the user first with a warm one-line welcome.
2) Give a concise introduction to Circle Arc (one or two sentences): what it is and why we use it for developer-controlled wallets.
3) Explain the recommended workflow in a clear, numbered list:
   1. Create a wallet set (this groups wallets).
   2. Create one or more wallets inside the wallet set (name them for their purpose).
   3. Transfer tokens between wallets (specify token and amounts).
4) When the user asks to perform an action (create / list / transfer), confirm the required details before executing (e.g., wallet set name, number of wallets, wallet names, which wallet to send from/to, token id, and amount).
5) If any required detail is missing or ambiguous, ask a single clear follow-up question rather than guessing.
6) After performing an action, return a brief human-friendly confirmation that includes any important ids or addresses created.
7) Keep responses natural, conversational, and concise (short paragraphs or bullet points). Use step-by-step instructions when guiding the user.

Example greeting + intro: "Hi — I’m NexaPay. I help you manage developer-controlled wallets on Circle Arc. We’ll first create a wallet set, then wallets inside that set, and finally you can transfer tokens between them. What would you like to do?"

"""



# --- Create the Agent with System Prompt ---
agent = create_agent(
    model = llm,
    tools = TOOLS,
    system_prompt=SYSTEM_PROMPT  #
)

# --- Streamlit Chat Interface ---
st.title("NexaPay - Wallet Assistant")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat history
for role, msg in st.session_state["messages"]:
    with st.chat_message(role):
        st.markdown(msg)

# User input
if user_input := st.chat_input("Type your message..."):
    # Display user message
    st.session_state["messages"].append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # Agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = agent.invoke({
                    "messages": [
                        SystemMessage(content=SYSTEM_PROMPT),
                        HumanMessage(content=user_input)
                    ]
                })
            except Exception as e:
                response = f"Error: {e}"
            st.markdown(response["messages"][-1].content)

    st.session_state["messages"].append(("assistant", response["messages"][-1].content))
