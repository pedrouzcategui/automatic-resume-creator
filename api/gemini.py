from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


class GeminiService:
    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        system_instruction: str = "",
        config: types.GenerateContentConfig | None = None,
    ):
        self.client = genai.Client()
        self.model = model
        self.config = config or types.GenerateContentConfig(
            system_instruction=system_instruction
        )

    def generate(self, prompt: str):
        return self.client.models.generate_content(
            model=self.model,
            config=self.config,
            contents=prompt,
        )


def generate_with_gemini(
    prompt: str,
    model: str = "gemini-2.5-flash",
    system_instruction: str = "",
    config: types.GenerateContentConfig | None = None,
):
    service = GeminiService(
        model=model,
        system_instruction=system_instruction,
        config=config,
    )
    return service.generate(prompt)