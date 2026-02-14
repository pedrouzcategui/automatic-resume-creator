from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class ChatGPTService:

    client = None

    def __init__(self):
        ChatGPTService._get_client()

    @classmethod
    def _get_client(cls):
        if cls.client is None:
            cls.client = OpenAI()
        return cls.client
    
    @staticmethod
    def generate(role: str = "user", prompt: str = "", model: str = "gpt-5-mini"):
        client = ChatGPTService._get_client()
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": role, "content": prompt}]
        )
        return response.choices[0].message.content

