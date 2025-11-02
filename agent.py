import speech_recognition as sr
import pyttsx3
from wallet_functions import (
    create_wallet_set,
    create_wallet,
    get_wallets,
    get_balance,
    transfer_token
)

# Initialize speech modules
recognizer = sr.Recognizer()
tts = pyttsx3.init()

def speak(text):
    tts.say(text)
    tts.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print("🗣️ You said:", text)
        return text.lower()
    except Exception as e:
        print("❌ Could not understand audio:", e)
        return ""

def handle_command(command):
    if "create wallet set" in command:
        speak("Creating a new wallet set.")
        create_wallet_set()
        speak("Wallet set created successfully.")
    
    elif "create wallet" in command:
        speak("Creating new wallets.")
        create_wallet()
        speak("Wallets created successfully.")
    
    elif "get wallets" in command:
        speak("Fetching all wallets.")
        get_wallets()
        speak("Wallets fetched.")
    
    elif "balance" in command:
        speak("Checking wallet balance.")
        get_balance()
        speak("Balance fetched successfully.")
    
    elif "transfer" in command:
        speak("Starting transfer.")
        transfer_token()
        speak("Transfer initiated successfully.")
    
    else:
        speak("Sorry, I didn't understand that command.")

if __name__ == "__main__":
    speak("Hello! I'm your Circle Wallet assistant. How can I help you today?")
    while True:
        command = listen()
        if "exit" in command or "quit" in command:
            speak("Goodbye!")
            break
        handle_command(command)
