import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class ChatBot:
    def __init__(self):
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set.")
        self.client = Groq(api_key=groq_api_key)
        self.messages = [{"role": "system", "content": "You are a virtual medical assistant. Based on the user's symptoms, ask relevant follow-up questions, suggest possible illnesses, and recommend steps for recovery. Ask one question at a time and wait for the user's response before proceeding."}]

    def get_response(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=self.messages,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
        )
        assistant_response = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": assistant_response})
        return assistant_response
