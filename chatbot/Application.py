import fastapi
from .TelegramBot import TelegramBot
from .Router import Router
from .models.Gemini import Gemini
from .IntentClassifier import IntentClassifier
from .TextGeneration import TextGeneration
import logging
from .utils import get_path


class Application:
    def __init__(self, server: fastapi.FastAPI):
        self._configure_logging()
        self.server = server
        self.model = Gemini() # We can edit the model here
        self.intent_classifier = IntentClassifier(model=self.model)
        self.text_generator = TextGeneration(model=self.model)

        self.router = Router(
            telegram_bot=TelegramBot(),
            intent_classifier=self.intent_classifier,
            text_generator=self.text_generator)
        self.register_endpoints()
    
    def _configure_logging(self):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler(get_path('app.log'))
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        logging.getLogger('').addHandler(file_handler)

    def register_endpoints(self):
        @self.server.get("/")
        def home():
            return "Success connected to server!"

        self.server.include_router(self.router)
