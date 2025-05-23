import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class NLPProcessor:
    def __init__(self, personality="You are an AI named KAIRO."):
        self.personality = personality

    def generate_response(self, input_text):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.personality},
                {"role": "user", "content": input_text}
            ]
        )
        return response.choices[0].message.cont
