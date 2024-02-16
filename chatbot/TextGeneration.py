from .Model import GenerativeModel

class TextGeneration:
    def __init__(self, model: GenerativeModel):
        self.model = model

    async def generate(self, prompt: str, generation_config: dict = None):
        return await self.model.generate_text(prompt, generation_config=generation_config)