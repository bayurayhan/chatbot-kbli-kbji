from typing import Any, Coroutine
from ..Model import GenerativeModel
# from langchain_openai import OpenAI
import openai

# TODO: Implement if needed
class OpenAIGPT(GenerativeModel):
    def __init__(self):
        self.model = openai.OpenAI()

    async def generate_text(self, prompt: list[dict], generation_config: dict = None) -> str:
        response = self.model.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=prompt,
            temperature=generation_config.get("temperature", 0.5) if generation_config else 0.5
        )
        return response.choices[0].message.content