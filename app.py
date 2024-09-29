from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
from translate_module.translator import TranslationService
from chat_module.chatbot import ChatBot
import os
import io

app = Flask(__name__)
CORS(app)

r = sr.Recognizer()
translator = TranslationService()
chatbot = ChatBot()

@app.route("/start_conversation", methods=["POST"])
def start_conversation():
    data = request.json
    language_code = data.get("language_code", "hi")
    initial_prompt = translator.translate("Please tell your name & location then describe your problem or symptoms.", language_code)
    return jsonify({"message": initial_prompt})

@app.route("/process_audio", methods=["POST"])
def process_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file found"}), 400

        audio_file = request.files['audio']
        audio_data = audio_file.read()
        
        # Convert the audio data to an AudioData object
        audio = sr.AudioData(audio_data, sample_rate=44100, sample_width=2)
        
        # Recognize the speech
        user_input = r.recognize_google(audio, language='hi')
        translated_input = translator.translate(user_input, 'en')
        
        assistant_response = chatbot.get_response(translated_input)
        translated_response = translator.translate(assistant_response, 'hi')
        
        # Check if the conversation should end
        conversation_ended = "thank you" in translated_input.lower() or "goodbye" in translated_input.lower()
        
        return jsonify({
            "user_input": user_input,
            "assistant_response": translated_response,
            "conversation_ended": conversation_ended
        })
    
    except sr.UnknownValueError:
        return jsonify({"error": "Speech was not understood"}), 400
    except sr.RequestError as e:
        return jsonify({"error": f"Could not request results from Google Speech Recognition service; {e}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)