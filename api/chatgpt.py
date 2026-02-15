import json
from typing import Any

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

    @classmethod
    def generate_response(
        cls,
        prompt: str | list[dict[str, Any]],
        model: str = "gpt-5-mini",
        instructions: str | None = None,
        **kwargs: Any,
    ):
        client = cls._get_client()

        if not hasattr(client, "responses"):
            raise RuntimeError(
                "OpenAI client does not support the Responses API. "
                "Upgrade the 'openai' package to a version that includes client.responses."
            )

        return client.responses.create(
            model=model,
            input=prompt,
            instructions=instructions,
            **kwargs,
        )

    @classmethod
    def generate_text(
        cls,
        prompt: str | list[dict[str, Any]],
        model: str = "gpt-5-mini",
        instructions: str | None = None,
        **kwargs: Any,
    ) -> str:
        response = cls.generate_response(
            prompt=prompt,
            model=model,
            instructions=instructions,
            **kwargs,
        )

        return response.output_text

    @staticmethod
    def _extract_json_object(text: str) -> str:
        candidate = text.strip()
        if candidate.startswith("```"):
            candidate = candidate.strip("`")
            candidate = candidate.replace("json\n", "", 1).strip()

        start = candidate.find("{")
        if start == -1:
            raise ValueError("No JSON object found in model output.")

        depth = 0
        in_string = False
        escape = False
        for index in range(start, len(candidate)):
            char = candidate[index]

            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
                continue

            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return candidate[start : index + 1]

        raise ValueError("Unterminated JSON object in model output.")

    @classmethod
    def generate_json(
        cls,
        prompt: str | list[dict[str, Any]],
        model: str = "gpt-5-mini",
        instructions: str | None = None,
        schema: dict[str, Any] | None = None,
        schema_name: str = "response",
        **kwargs: Any,
    ) -> dict[str, Any]:
        json_instruction = (
            "Return ONLY valid JSON. Do not wrap it in markdown code fences. "
            "Do not include commentary."
        )

        effective_instructions = json_instruction if not instructions else f"{instructions}\n\n{json_instruction}"

        response_kwargs: dict[str, Any] = dict(kwargs)
        if schema is not None:
            response_kwargs["text"] = {
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "strict": True,
                    "schema": schema,
                }
            }
        else:
            response_kwargs["text"] = {
                "format": {
                    "type": "json_object",
                }
            }

        text = cls.generate_text(
            prompt=prompt,
            model=model,
            instructions=effective_instructions,
            **response_kwargs,
        )

        json_text = cls._extract_json_object(text)
        try:
            parsed = json.loads(json_text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Failed to parse JSON from model output: {exc}") from exc

        if not isinstance(parsed, dict):
            raise ValueError("Model output JSON was not an object.")

        return parsed
    
    @staticmethod
    def generate(role: str = "user", prompt: str = "", model: str = "gpt-5-mini"):
        response = ChatGPTService.generate_response(
            prompt=[{"role": role, "content": prompt}],
            model=model,
        )
        return response.output_text

