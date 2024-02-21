import g4f
from ..Model import *
from ..utils import *


# NOTE: This model is for educational purposed only
class GPT4Free(GenerativeModel):
    def __init__(self, name) -> None:
        self.provider = g4f.Provider.Bing

    async def generate_text(self, prompt: list[dict], generation_config: dict = None) -> str:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.gpt_4,
            messages=prompt,
            provider=self.provider
        )
        response = remove_emojis(response)
        return response
