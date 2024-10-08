import sys
import os
import speech_recognition as sr


# Add the paths to the module directories
sys.path.append('./translate_module')
sys.path.append('./chat_module')

from translate_module.translator import TranslationService
from chat_module.chatbot import ChatBot

# Initialize speech recognition
r = sr.Recognizer()

def get_audio_input(language_code):
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=10, phrase_time_limit=10)
        return r.recognize_google(audio, language=language_code)
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand that. Please try again.")
        return get_audio_input(language_code)
    except sr.RequestError:
        print("Sorry, there was an error with the speech recognition service. Please try again.")
        return get_audio_input(language_code)
    except ValueError:
        print("Sorry, I didn't receive any audio input. Please try again.")
        return get_audio_input(language_code)

def handle_medical_conversation(language_code):
    translator = TranslationService()
    chatbot = ChatBot()

    initial_prompt = translator.translate("Please tell your name & location then describe your problem or symptoms.", language_code)
    translator.text_to_speech(initial_prompt, language_code)
    print(f"PureCure BOT: {initial_prompt}")
    
    while True:
        user_input = get_audio_input(language_code)
        translated_input = translator.translate(user_input, 'en')
        print(f"User said: {user_input}")
        print(f"Translated: {translated_input}")

        assistant_response = chatbot.get_response(translated_input)
        translated_response = translator.translate(assistant_response, language_code)
        print(f"Assistant response: {assistant_response}")
        print(f"Translated response: {translated_response}")
        
        translator.text_to_speech(translated_response, language_code)

        if "thank you" in translated_input.lower() or "goodbye" in translated_input.lower():
            farewell = translator.translate("You're welcome. Take care and get well soon!", language_code)
            translator.text_to_speech(farewell, language_code)
            break

if __name__ == "__main__":
    language_code = 'hi'  # Hindi
    handle_medical_conversation(language_code)