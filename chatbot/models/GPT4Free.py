import g4f
from ..Model import *
from ..utils import *


# NOTE: This model is for educational purposed only
class GPT4Free(GenerativeModel):
    def __init__(self) -> None:
        self.provider = g4f.Provider.OpenaiChat

    async def generate_text(self, prompt: any, generation_config: dict = None):
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.gpt_35_turbo,
            messages=prompt,
            provider=self.provider
        )
        response = remove_emojis(response)
        return response
