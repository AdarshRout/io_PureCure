import os
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
from groq import Groq
import googletrans
from gtts import gTTS
import pygame

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

# Initialize Google Translate
translator = googletrans.Translator()

# Initialize pygame for audio playback
pygame.mixer.init()

def get_audio_input(language_code):
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=10, phrase_time_limit=10)
        return r.recognize_google(audio, language=language_code)
    except sr.UnknownValueError:
        generate_audio_response("Sorry, I couldn't understand that. Please try again.", language_code)
        return get_audio_input(language_code)
    except sr.RequestError:
        generate_audio_response("Sorry, there was an error with the speech recognition service. Please try again.", language_code)
        return get_audio_input(language_code)
    except ValueError:
        generate_audio_response("Sorry, I didn't receive any audio input. Please try again.", language_code)
        return get_audio_input(language_code)

def generate_audio_response(text, language_code):
    tts = gTTS(text=text, lang=language_code)
    tts.save("output.mp3")
    
    pygame.mixer.music.load("output.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    return text

def translate_text(text, target_language):
    result = translator.translate(text, dest=target_language)
    return result.text

def handle_medical_conversation(language_code):
    messages = [{"role": "system", "content": "You are a virtual medical assistant. Based on the user's symptoms, ask relevant follow-up questions, suggest possible illnesses, and recommend steps for recovery. Ask one question at a time and wait for the user's response before proceeding."}]

    initial_prompt = translate_text("Please describe your problem or symptoms.", language_code)
    generate_audio_response(initial_prompt, language_code)
    print(f"PureCure BOT: {initial_prompt}")
    
    while True:
        user_input = get_audio_input(language_code)
        translated_input = translate_text(user_input, 'en')
        messages.append({"role": "user", "content": translated_input})
        print(f"User said: {user_input}")
        print(f"Translated: {translated_input}")

        # Use Groq to generate the assistant's response
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
        )
        
        assistant_response = response.choices[0].message.content
        translated_response = translate_text(assistant_response, language_code)
        print(f"Assistant response: {assistant_response}")
        print(f"Translated response: {translated_response}")
        assistant_audio_response = generate_audio_response(translated_response, language_code)

        messages.append({"role": "assistant", "content": assistant_response})

        # Check if the conversation is complete
        if "thank you" in translated_input.lower() or "goodbye" in translated_input.lower():
            farewell = translate_text("You're welcome. Take care and get well soon!", language_code)
            generate_audio_response(farewell, language_code)
            break

if __name__ == "__main__":
    # You can change this to any supported language code
    language_code = 'hi'  # Hindi
    handle_medical_conversation(language_code)