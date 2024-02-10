from .Model import GenerativeModel

class TextGeneration:
    def __init__(self, model: GenerativeModel):
        self.model = model

    def generate(self, prompt: str):
        return self.model.generate_text(prompt)