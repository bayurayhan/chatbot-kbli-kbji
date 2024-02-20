from typing import Any, Coroutine
from ..Model import GenerativeModel
# from langchain_openai import OpenAI
import openai

# TODO: Implement if needed
class OpenAIGPT(GenerativeModel):
    def __init__(self, name="gpt-3-turbo", temperature=0.5, top_p=0.5, top_k=40, max_output_tokens=4000):
        self.name = name
        self.model = openai.OpenAI()
        self.temperature = temperature

    async def generate_text(self, prompt: list[dict], generation_config: dict = None) -> str:
        response = self.model.chat.completions.create(
            model=self.name,
            messages=prompt,
            temperature=generation_config.get("temperature", 0.5) if generation_config else self.temperature
        )
        return response.choices[0].message.content