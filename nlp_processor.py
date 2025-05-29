import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv(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)

class NLPProcessor:
    def __init__(self, personality="You are an AI named KAIRO."):
        self.personality = personality

    def generate_response(self, input_text):
        response = openai.ChatCompletion.create(
            model="gpt-4", # Ensure you have access to gpt-4 or change to a suitable model
            messages=[
                {"role": "system", "content": self.personality},
                {"role": "user", "content": input_text}
            ]
        )
        return response.choices[0].message.content # Corrected typo
