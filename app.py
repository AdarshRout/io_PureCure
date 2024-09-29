# from flask import Flask, request, jsonify, send_file
# from flask_cors import CORS
# import speech_recognition as sr
# from translate_module.translator import TranslationService
# from chat_module.chatbot import ChatBot
# import os
# import io
# import tempfile
# import logging

# app = Flask(__name__)
# CORS(app)

# # Set up logging
# logging.basicConfig(level=logging.DEBUG)

# r = sr.Recognizer()
# translator = TranslationService()
# chatbot = ChatBot()

# @app.route("/start_conversation", methods=["POST"])
# def start_conversation():
#     try:
#         data = request.json
#         language_code = data.get("language_code", "hi")
#         initial_prompt = translator.translate("Please tell your name & location then describe your problem or symptoms.", language_code)
        
#         # Generate speech for the initial prompt
#         speech_file = translator.text_to_speech(initial_prompt, language_code)
        
#         return jsonify({
#             "message": initial_prompt,
#             "audio_url": f"/get_audio/{speech_file}"
#         })
#     except Exception as e:
#         logging.error(f"Error in start_conversation: {e}")
#         return jsonify({"error": str(e)}), 500

# @app.route("/get_audio/<filename>", methods=["GET"])
# def get_audio(filename):
#     try:
#         return send_file(filename, mimetype="audio/mpeg")
#     except Exception as e:
#         logging.error(f"Error in get_audio: {e}")
#         return jsonify({"error": str(e)}), 500

# @app.route("/process_audio", methods=["POST"])
# def process_audio():
#     try:
#         if 'audio' not in request.files:
#             return jsonify({"error": "No audio file found"}), 400

#         audio_file = request.files['audio']
        
#         # Save the audio file temporarily
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
#             audio_file.save(temp_audio.name)
#             temp_audio_path = temp_audio.name

#         # Use the temporary file for speech recognition
#         with sr.AudioFile(temp_audio_path) as source:
#             audio = r.record(source)
        
#         # Recognize the speech
#         user_input = r.recognize_google(audio, language='hi')
#         translated_input = translator.translate(user_input, 'en')
        
#         assistant_response = chatbot.get_response(translated_input)
#         translated_response = translator.translate(assistant_response, 'hi')
        
#         # Generate speech for the assistant's response
#         speech_file = translator.text_to_speech(translated_response, 'hi')
        
#         # Check if the conversation should end
#         conversation_ended = "thank you" in translated_input.lower() or "goodbye" in translated_input.lower()
        
#         # Clean up the temporary audio file
#         os.unlink(temp_audio_path)
        
#         return jsonify({
#             "user_input": user_input,
#             "assistant_response": translated_response,
#             "conversation_ended": conversation_ended,
#             "audio_url": f"/get_audio/{speech_file}"
#         })
    
#     except sr.UnknownValueError:
#         return jsonify({"error": "Speech was not understood"}), 400
#     except sr.RequestError as e:
#         logging.error(f"Google Speech Recognition service error: {e}")
#         return jsonify({"error": f"Could not request results from Google Speech Recognition service; {e}"}), 500
#     except Exception as e:
#         logging.error(f"Error in process_audio: {e}")
#         return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     app.run(port=5000, debug=True)


from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import speech_recognition as sr
from translate_module.translator import TranslationService
from chat_module.chatbot import ChatBot
import os
import io
import tempfile
import logging

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})

# Set up logging
logging.basicConfig(level=logging.DEBUG)

r = sr.Recognizer()
translator = TranslationService()
chatbot = ChatBot()


@app.route("/start_conversation", methods=["POST"])
def start_conversation():
    try:
        initial_prompt = "कृपया अपना नाम, स्थान और लक्षण बताएं।"
        speech_file = translator.text_to_speech(initial_prompt, 'hi')
        
        return jsonify({
            "message": initial_prompt,
            "audio_url": f"http://127.0.0.1:5000/get_audio/{os.path.basename(speech_file)}"
        })
    except Exception as e:
        logging.error(f"Error in start_conversation: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/get_audio/<filename>", methods=["GET"])
def get_audio(filename):
    try:
        return send_file(filename, mimetype="audio/mpeg")
    except Exception as e:
        logging.error(f"Error in get_audio: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/process_audio", methods=["POST"])
def process_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file found"}), 400

        audio_file = request.files['audio']
        
        # Save the audio file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            audio_file.save(temp_audio.name)
            temp_audio_path = temp_audio.name

        # Use the temporary file for speech recognition
        with sr.AudioFile(temp_audio_path) as source:
            audio = r.record(source)
        
        # Recognize the speech
        user_input = r.recognize_google(audio, language='hi')
        translated_input = translator.translate(user_input, 'en')
        
        assistant_response = chatbot.get_response(translated_input)
        translated_response = translator.translate(assistant_response, 'hi')
        
        # Generate speech for the assistant's response
        speech_file = translator.text_to_speech(translated_response, 'hi')
        
        # Check if the conversation should end
        conversation_ended = "thank you" in translated_input.lower() or "goodbye" in translated_input.lower()
        
        # Clean up the temporary audio file
        os.unlink(temp_audio_path)
        
        return jsonify({
            "user_input": user_input,
            "assistant_response": translated_response,
            "conversation_ended": conversation_ended,
            "audio_url": f"127.0.0.1:5000/get_audio/{os.path.basename(speech_file)}"
        })
    
    except sr.UnknownValueError:
        return jsonify({"error": "Speech was not understood"}), 400
    except sr.RequestError as e:
        logging.error(f"Google Speech Recognition service error: {e}")
        return jsonify({"error": f"Could not request results from Google Speech Recognition service; {e}"}), 500
    except Exception as e:
        logging.error(f"Error in process_audio: {e}")
        return jsonify({"error": str(e)}), 500
    

@app.after_request
def add_header(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


if __name__ == "__main__":
    app.run(port=5000, debug=True)