import fastapi
from .TelegramBot import TelegramBot
from .Router import Router
from .models.Gemini import Gemini
from .IntentClassifier import IntentClassifier
from .TextGeneration import TextGeneration

class Application:
    def __init__(self, server: fastapi.FastAPI):
        self.server = server
        self.model = Gemini() # We can edit the model here
        self.intent_classifier = IntentClassifier(model=self.model)
        self.text_generator = TextGeneration(model=self.model)

        self.router = Router(
            telegram_bot=TelegramBot(),
            intent_classifier=self.intent_classifier,
            text_generator=self.text_generator)
        self.register_endpoints()

    def register_endpoints(self):
        @self.server.get("/")
        def home():
            return "Success connected to server!"

        self.server.include_router(self.router)
