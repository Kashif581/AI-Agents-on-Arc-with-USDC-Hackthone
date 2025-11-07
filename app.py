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


# # --- Initialize LLM ---
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    google_api_key=""
)



TOOLS = [
    tool_create_wallet_set,
    tool_create_wallets,
    tool_list_wallets,
    tool_transfer_token,
    tool_get_wallet_balance
]



# # --- Custom System Prompt ---
SYSTEM_PROMPT = """You are NexaPay, a friendly AI assistant helping users manage wallets using Circle's API.

If this is the user's first message, greet them and introduce Circle Arc blockchain with these steps:
1. Create a wallet set.
2. Create wallets.
3. Transfer tokens.

Otherwise, respond directly to their requests without repeating the introduction.

You can:
- Create wallet sets and wallets
- List existing wallets and balances
- Transfer tokens

🗣 Speak naturally and conversationally.
🤔 If something is missing (like wallet set name, number of wallets, or wallet names), ask a clear follow-up question instead of guessing.
Keep responses short, helpful, and step-by-step.

"""



# # --- Create the Agent with System Prompt ---
agent = create_agent(
    model = llm,
    tools = TOOLS,
    system_prompt=SYSTEM_PROMPT  #
)


import streamlit as st
from langchain.messages import SystemMessage, HumanMessage

st.title("NexaPay - Wallet Assistant")

# --- File Upload Section ---
st.subheader("Upload your electricity bill (PNG)")
uploaded_file = st.file_uploader("Choose a bill image", type=["png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Bill", use_column_width=True)
    st.success("Bill uploaded successfully!")

# --- Chat Section ---
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
                # Optional: You can pass the uploaded image bytes to your agent
                if uploaded_file is not None:
                    image_bytes = uploaded_file.read()
                    response = agent.invoke({
                        "messages": [
                            SystemMessage(content=SYSTEM_PROMPT),
                            HumanMessage(content=user_input),
                        ],
                        "image": image_bytes  # if your agent supports image input
                    })
                else:
                    response = agent.invoke({
                        "messages": [
                            SystemMessage(content=SYSTEM_PROMPT),
                            HumanMessage(content=user_input)
                        ]
                    })

                ai_msg = response["messages"][-1].content
                ai_text = ai_msg[0].get("text", "") if isinstance(ai_msg, list) else str(ai_msg)

            except Exception as e:
                ai_text = f"Error: {e}"

            st.markdown(ai_text)

    st.session_state["messages"].append(("assistant", ai_text))

