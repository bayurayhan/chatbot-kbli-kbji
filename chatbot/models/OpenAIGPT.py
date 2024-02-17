from typing import Any, Coroutine
from ..Model import GenerativeModel
from langchain_openai import ChatOpenAI

# TODO: Implement if needed
class OpenAIGPT(GenerativeModel):
    def __init__(self):
        self.model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

    async def generate_text(self, prompt: any, generation_config: dict = None) -> str:
        response = self.model.invoke()