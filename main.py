import speech_recognition as sr
import requests
import json
import pyttsx3
import time
import re
import keyboard  # For hotkey functionality

# Initialize the speech recognition and TTS engines
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Set up Ollama API endpoint
OLLAMA_API = "http://localhost:11434/api/generate"

# Configure hotkey for push-to-talk (default: Ctrl+Space)
HOTKEY = "ctrl+space"

# Set this to True for continuous listening mode without any key press
CONTINUOUS_MODE = False

# Function to send prompt to Ollama and get response
def query_melonia(prompt):
    data = {
        "model": "melonia",
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(OLLAMA_API, json=data)
    if response.status_code == 200:
        result = response.json()
        # Remove any <think> tags that might be in the response
        cleaned_response = re.sub(r'<think>.*?</think>', '', result['response'], flags=re.DOTALL)
        return cleaned_response
    else:
        return f"Error: {response.status_code}"

# Function to speak the response
def speak(text):
    print(f"Melonia: {text}")
    engine.say(text)
    engine.runAndWait()

def listen_for_command():
    with sr.Microphone() as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        try:
            # Visual indicator that we're listening
            print("Listening... (speak now)")
            
            # Listen for audio
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            # Convert speech to text
            command = recognizer.recognize_google(audio)
            print(f"You: {command}")
            
            # Process the command
            response = query_melonia(command)
            speak(response)
            
            return True
            
        except sr.WaitTimeoutError:
            print("No speech detected.")
            return True
        except sr.UnknownValueError:
            print("Could not understand audio")
            return True
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

def hotkey_callback():
    print("\nHotkey pressed! Listening for command...")
    listen_for_command()

def main():
    print("Melonia Voice Assistant is starting...")
    
    # First, test if Ollama is running
    try:
        test_response = query_melonia("Hello")
        print(f"Ollama test response: {test_response}")
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        print("Please make sure Ollama is running with 'melonia' model loaded")
        return
    
    if CONTINUOUS_MODE:
        print("Running in continuous listening mode...")
        running = True
        while running:
            running = listen_for_command()
            time.sleep(0.5)  # Short pause to prevent high CPU usage
    else:
        print(f"Running in push-to-talk mode. Press {HOTKEY} to activate Melonia.")
        keyboard.add_hotkey(HOTKEY, hotkey_callback)
        
        # Keep the program running
        keyboard.wait('esc')  # Exit when ESC is pressed
        print("Exiting Melonia Assistant.")

if __name__ == "__main__":
    main()