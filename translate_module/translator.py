from googletrans import Translator
from gtts import gTTS
import os

class TranslationService:
    def __init__(self):
        self.translator = Translator()

    def translate(self, text, target_language):
        result = self.translator.translate(text, dest=target_language)
        return result.text

    def text_to_speech(self, text, language_code):
        tts = gTTS(text=text, lang=language_code)
        tts.save("output.mp3")
        return "output.mp3"