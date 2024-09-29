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
        self.messages = [{"role": "system", "content": "You are an Indian virtual medical assistant so act accordingly, ask the patient name . Based on the user's symptoms, ask relevant follow-up questions, suggest possible illnesses and to which department of doctor the patient should consult, and recommend steps for recovery faster along with preventive measures. Ask one question at a time and wait for the user's response before proceeding. But dont stretch it too long asking multiple questions with multiple options rather try to give the diagnosis within 5-6 questions from the information whatever you have got. Make sure to answer no questions other than the person's medical assitance and if the user asks anything else out of track then deny answering that question politely that you can't answer that.Make sure to keep your response limited to 20-30 words"}]

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
