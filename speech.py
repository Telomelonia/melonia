import speech_recognition as sr
import pyttsx3
import subprocess
import json

# Setup speech recognition
recognizer = sr.Recognizer()

# Setup text-to-speech
engine = pyttsx3.init()
engine.setProperty('rate', 180)  # Speed of speech
engine.setProperty('volume', 0.9)  # Volume

def speak(text):
    """Have Jarvis speak the response"""
    print(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listen for user commands"""
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        
    try:
        print("Processing...")
        command = recognizer.recognize_google(audio)
        print(f"You: {command}")
        return command
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return None
    except sr.RequestError:
        speak("I'm having trouble connecting to the speech recognition service.")
        return None
def clean_jarvis_response(response):
    """Remove thinking process from Jarvis responses"""
    # Check if there's a thinking section
    if "<think>" in response and "</think>" in response:
        # Find the starting position after </think>
        start_pos = response.find("</think>") + len("</think>")
        # Return only what comes after the thinking section
        return response[start_pos:].strip()
    else:
        # No thinking section, return as is
        return response.strip()
def ask_jarvis(prompt):
    """Send prompt to Ollama Jarvis model and get response"""
    result = subprocess.run(
        ["ollama", "run", "jarvis-deepseek", prompt],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

# Main interaction loop
speak("Jarvis online. How may I assist you today, sir?")

while True:
    command = listen()
    if command:
        if "goodbye" in command.lower() or "bye" in command.lower():
            speak("Shutting down. Have a good day, sir.")
            break
        response = ask_jarvis(command)

        clean_response = clean_jarvis_response(response)
        speak(clean_response)