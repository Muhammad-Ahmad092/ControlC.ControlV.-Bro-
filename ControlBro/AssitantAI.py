import os
import webbrowser
import datetime
import random
import whisper
import sounddevice as sd
import numpy as np
import wavio
import google.generativeai as genai
from config import gemini_api_key

# Configure Gemini
genai.configure(api_key=gemini_api_key)
assistant_name = "ControlC ControlV Bro"
chatStr = ""

# Load Whisper model
whisper_model = whisper.load_model("base")

# -------------------- Voice Output --------------------
try:
    import pyttsx3
    engine = pyttsx3.init()
    def say(text):
        engine.say(text)
        engine.runAndWait()
except ImportError:
    def say(text):
        os.system(f'say "{text}"')  # Fallback for macOS

# -------------------- Voice Input via Whisper --------------------
def record_audio(filename="temp.wav", duration=5, fs=44100):
    print("Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    wavio.write(filename, recording, fs, sampwidth=2)
    print("Recording complete.")

def takeCommand():
    record_audio()
    print("Transcribing with Whisper...")
    result = whisper_model.transcribe("temp.wav")
    print("You said:", result["text"])
    return result["text"]

# -------------------- Gemini Chat --------------------
def chat_with_gemini(query):
    global chatStr
    chatStr += f"You: {query}\n{assistant_name}: "

    try:
        model = genai.GenerativeModel("models/chat-bison-001")
        convo = model.start_chat(history=[
            {"role": "user", "parts": [query]}
        ])
        response = convo.send_message(query)
        reply = response.text.strip()

        chatStr += reply + "\n"
        say(reply)
        return reply

    except Exception as e:
        print("Gemini Error:", e)
        say("Sorry, I encountered a problem.")
        return ""

# -------------------- AI File Writer --------------------
def ai(prompt):
    try:
        model = genai.GenerativeModel('models/chat-bison-001')
        response = model.generate_content(prompt)
        answer = response.text.strip()

        filename = prompt[:30].replace(" ", "_") + ".txt"
        os.makedirs("GeminiOutputs", exist_ok=True)

        with open(f"GeminiOutputs/{filename}", "w") as f:
            f.write(f"Prompt: {prompt}\n\nResponse:\n{answer}")

        say("I saved the response to a file.")
    except Exception as e:
        print("AI Error:", e)
        say("Something went wrong while saving the file.")

# -------------------- Main Program --------------------
if __name__ == '__main__':
    print(f"Welcome to {assistant_name}")
    say(f"Hello! I am {assistant_name}, your AI assistant.")

    while True:
        print("Listening...")
        query = takeCommand()

        # Basic Commands
        sites = [["youtube", "https://www.youtube.com"], ["wikipedia", "https://www.wikipedia.com"], ["google", "https://www.google.com"]]
        for site in sites:
            if f"open {site[0]}" in query.lower():
                say(f"Opening {site[0]}...")
                webbrowser.open(site[1])

        if "open music" in query.lower():
            musicPath = "F:/YourMusicFolder/sample.mp3"  # Replace with valid path
            os.system(f'start "" "{musicPath}"')

        elif "what's the time" in query.lower() or "tell me the time" in query.lower():
            hour = datetime.datetime.now().strftime("%H")
            minute = datetime.datetime.now().strftime("%M")
            say(f"Time is {hour} hours and {minute} minutes")

        elif "reset chat" in query.lower():
            chatStr = ""
            say("Chat history cleared.")

        elif "quit" in query.lower() or "exit" in query.lower():
            say("Goodbye, shutting down.")
            break

        elif "using artificial intelligence" in query.lower():
            ai(query)

        else:
            print("Chatting with Gemini...")
            chat_with_gemini(query)
