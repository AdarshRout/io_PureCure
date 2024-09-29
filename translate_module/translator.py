from deep_translator import GoogleTranslator
from gtts import gTTS
import io
import pygame

class TranslationService:
    def __init__(self):
        self.translator = GoogleTranslator(source='auto', target='en')
        pygame.mixer.init()

    def translate(self, text, target_language):
        self.translator.target = target_language
        return self.translator.translate(text)

    def text_to_speech(self, text, language_code):
        speech = gTTS(text=text, lang=language_code)
        fp = io.BytesIO()
        speech.write_to_fp(fp)
        fp.seek(0)
        pygame.mixer.music.load(fp)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)


            