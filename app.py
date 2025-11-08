
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage

# Import wallet tools
from wallet_tools import (
    tool_create_wallet_set,
    tool_create_wallets,
    tool_list_wallets,
    tool_transfer_token,
    tool_get_wallet_balance
)

# ------------------ Streamlit UI ------------------

st.set_page_config(page_title="NexaPay - Wallet Assistant", page_icon="💳")
st.title("💳 NexaPay - AI Wallet Assistant")

# --- Sidebar for Environment Inputs ---
st.sidebar.title("🔐 Environment Configuration")
st.sidebar.markdown("Enter your environment secrets below:")

circle_api_key =  st.sidebar.text_input("Enter CIRCLE_API_KEY", type="password")
entity_secret = st.sidebar.text_input("Enter ENTITY_SECRET", type="password")
gemini_api_key = st.sidebar.text_input("Enter GEMINI_API_KEY", type="password")

if gemini_api_key and entity_secret and circle_api_key:
    st.session_state["CIRCLE_API_KEY"] = circle_api_key
    st.session_state["ENTITY_SECRET"] = entity_secret
    st.session_state["GEMINI_API_KEY"] = gemini_api_key
   
    
    st.sidebar.success("✅ Keys saved for this session.")
else:
    st.sidebar.warning("⚠️ Please enter your CIRCLE_API_KEY, ENTITY_SECRET and GEMINI_API_KEY to continue.")
    st.stop()  # Stop app until keys are entered

# ------------------ Initialize LLM ------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    google_api_key=st.session_state["GEMINI_API_KEY"]
)

TOOLS = [
    tool_create_wallet_set,
    tool_create_wallets,
    tool_list_wallets,
    tool_transfer_token,
    tool_get_wallet_balance
]

# ------------------ System Prompt ------------------

SYSTEM_PROMPT = """You are NexaPay — a friendly AI assistant that helps users manage wallets and transfers on Circle’s Arc blockchain.

If this is the user’s first message:
- Greet them warmly.
- Briefly introduce Arc blockchain and NexaPay’s main features:
  1. Create a wallet set.
  2. Create wallets.
  3. Transfer tokens between wallets.

Otherwise, respond directly to their request.

Capabilities:
- Create wallet sets and wallets
- Transfer tokens

Transfer rule:
Before transferring, always ask for:
• Source wallet ID  
• Destination wallet address  
• Amount to transfer  

Style:
- Conversational, concise, step-by-step.
- Never ask for private keys or secrets.
- End responses with a clear next step (e.g., “Would you like to create a wallet set or make a transfer?”).
"""

# ------------------ Create Agent ------------------

agent = create_agent(
    model=llm,
    tools=TOOLS,
    system_prompt=SYSTEM_PROMPT
)

# ------------------ File Upload (Optional) ------------------

st.subheader("📄 Upload your electricity bill (optional, PNG)")
uploaded_file = st.file_uploader("Choose a bill image", type=["png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Bill", use_column_width=True)
    st.success("✅ Bill uploaded successfully!")

# ------------------ Chat Interface ------------------

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat history
for role, msg in st.session_state["messages"]:
    with st.chat_message(role):
        st.markdown(msg)

# User input box
if user_input := st.chat_input("Type your message..."):
    # Save user message
    st.session_state["messages"].append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI response
    with st.chat_message("assistant"):
        with st.spinner("💭 Thinking..."):
            try:
                payload = {
                    "messages": [
                        SystemMessage(content=SYSTEM_PROMPT),
                        HumanMessage(content=user_input)
                    ]
                }

                if uploaded_file is not None:
                    payload["image"] = uploaded_file.read()

                response = agent.invoke(payload)

                # Handle different response formats
                ai_msg = response["messages"][-1].content
                ai_text = ai_msg[0].get("text", "") if isinstance(ai_msg, list) else str(ai_msg)

            except Exception as e:
                ai_text = f"❌ Error: {e}"

            st.markdown(ai_text)

    st.session_state["messages"].append(("assistant", ai_text))
