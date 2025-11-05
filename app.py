import streamlit as st
import speech_recognition as sr
from elevenlabs import ElevenLabs
from dotenv import load_dotenv
import os
from langchain_core.messages import HumanMessage
from agent import workflow  # your LangGraph agent

# --- Load environment ---
load_dotenv()
elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

st.title("NexaPay: Next-gen Payments and Wallet Management")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

recognizer = sr.Recognizer()
mic = sr.Microphone()

# --- Record user speech ---
if st.button("🎤 Speak Now"):
    with mic as source:
        st.write("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        # --- Speech to Text ---
        user_text = recognizer.recognize_google(audio)
        st.write(f"You said: {user_text}")
        st.session_state.chat_history.append(("You", user_text))

        # --- Pass to LangGraph Agent ---
        state = {"messages": [HumanMessage(content=user_text)]}
        result = workflow.invoke(state)
        ai_message = result["messages"][-1].content
        st.session_state.chat_history.append(("Agent", ai_message))

        # --- ElevenLabs TTS for dynamic AI reply ---
        audio_gen = elevenlabs.text_to_speech.convert(
            voice_id="JBFqnCBsd6RMkjVDRZzb",  # Rachel voice (multilingual)
            model_id="eleven_multilingual_v2",
            text=ai_message,
            output_format="mp3_44100_128",
        )

        # --- Play directly in Streamlit ---
        audio_bytes = b"".join(audio_gen)
        st.audio(audio_bytes, format="audio/mp3")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

# --- Display chat history ---
st.markdown("### Chat History")
for sender, msg in st.session_state.chat_history:
    if sender == "You":
        st.markdown(f"**🧍 You:** {msg}")
    else:
        st.markdown(f"**🤖 Agent:** {msg}")
