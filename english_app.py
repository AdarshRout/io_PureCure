import os
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Initialize speech recognition and synthesis
r = sr.Recognizer()
engine = pyttsx3.init()

# Initialize Groq client for language model
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

client = Groq(api_key=groq_api_key)

def get_audio_input():
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=10, phrase_time_limit=10)
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        generate_audio_response("Sorry, I couldn't understand that. Please try again.")
        return get_audio_input()
    except sr.RequestError:
        generate_audio_response("Sorry, there was an error with the speech recognition service. Please try again.")
        return get_audio_input()
    except ValueError:
        generate_audio_response("Sorry, I didn't receive any audio input. Please try again.")
        return get_audio_input()

def generate_audio_response(text):
    engine.say(text)
    engine.runAndWait()
    return text

def handle_medical_conversation():
    messages = [{"role": "system", "content": "You are a virtual medical assistant so act accordingly, ask the patient name . Based on the user's symptoms, ask relevant follow-up questions, suggest possible illnesses, and recommend steps for recovery. Ask one question at a time and wait for the user's response before proceeding. But dont stretch it too long and try to give the diagnosis within 5 questions from the information whatever you have got"}]

    generate_audio_response("Please describe your problem or symptoms.")
    print("PureCure BOT: What is your name ? Please describe your problem or symptoms.")
    
    while True:
        user_input = get_audio_input()
        messages.append({"role": "user", "content": user_input})
        print(f"User said: {user_input}")

        # Use Groq to generate the assistant's response
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
        )
        
        assistant_response = response.choices[0].message.content
        print(f"Assistant response: {assistant_response}")
        assistant_audio_response = generate_audio_response(assistant_response)

        messages.append({"role": "assistant", "content": assistant_audio_response})

        # Check if the conversation is complete
        if "thank you" in user_input.lower() or "goodbye" in user_input.lower():
            generate_audio_response("You're welcome. Take care and get well soon!")
            break

if __name__ == "__main__":
    handle_medical_conversation()