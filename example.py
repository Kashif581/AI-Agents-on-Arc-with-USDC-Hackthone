# from dotenv import load_dotenv
# from elevenlabs.client import ElevenLabs
# from elevenlabs.play import play
# import os

# load_dotenv()

# elevenlabs = ElevenLabs(
#   api_key="sk_3673c6637595073ec0d5a8be1b0b3c2ee491e721ec98133d"
# )

# audio = elevenlabs.text_to_speech.convert(
#     text="The first move is what sets everything in motion.",
#     voice_id="JBFqnCBsd6RMkjVDRZzb",
#     model_id="eleven_multilingual_v2",
#     output_format="mp3_44100_128",
# )

# play(audio)

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import os
load_dotenv()

elevenlabs = ElevenLabs(
    api_key="sk_3673c6637595073ec0d5a8be1b0b3c2ee491e721ec98133d",
)

prompt = """
You are a friendly and efficient virtual assistant for Circle Arc Blockchain.
Your role is to assist customers by answering questions about the company's products, services,
and documentation. You should use the provided knowledge base to offer accurate and helpful responses.

Tasks:
- Answer Questions: Provide clear and concise answers based on the available information.
- Clarify Unclear Requests: Politely ask for more details if the customer's question is not clear.

Guidelines:
- Maintain a friendly and professional tone throughout the conversation.
- Be patient and attentive to the customer's needs.
- If unsure about any information, politely ask the customer to repeat or clarify.
- Avoid discussing topics unrelated to the company's products or services.
- Aim to provide concise answers. Limit responses to a couple of sentences and let the user guide you on where to provide more detail.
"""

response = elevenlabs.conversational_ai.agents.create(
    name="My voice agent",
    tags=["test"], # List of tags to help classify and filter the agent
    conversation_config={
        "tts": {
            "voice_id": "21m00Tcm4TlvDq8ikWAM",
            "model_id": "eleven_flash_v2"
        },
        "agent": {
            "first_message": "Hi, this is Rachel from Circle support. How can I help you today?",
            "prompt": {
                "prompt": prompt,
            }
        }
    }
)

print("Agent created with ID:", response.agent_id)
