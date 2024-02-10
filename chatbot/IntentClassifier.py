from enum import Enum
from .Model import GenerativeModel

class Intent(str, Enum):
    MENCARI_KODE = "mencari kode"
    MENJELASKAN_KODE = "menjelaskan kode"
    TIDAK_RELEVAN = "tidak relevan"

class IntentClassifier:
    def __init__(self, model: GenerativeModel):
        self.model = model

    def predict(self, message: str) -> str:
        pass

