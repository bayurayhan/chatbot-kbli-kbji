import fastapi
from .TelegramBot import TelegramBot
from .Router import Router
import models
from .IntentClassifier import IntentClassifier
from .TextGeneration import TextGeneration
import logging
import logging.config
from .utils import get_path


class Application:
    def __init__(self, server: fastapi.FastAPI):
        self._configure_logging()
        self.server = server

        generative_model = models.Gemini() # We can edit the model here
        embedding_model = models.OpenAIEmbedding()

        intent_classifier = IntentClassifier(model=generative_model)
        text_generator = TextGeneration(model=generative_model)

        self.router = Router(
            telegram_bot=TelegramBot(),
            intent_classifier=intent_classifier,
            text_generator=text_generator)
        self.register_endpoints()
    
    def _configure_logging(self):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler(get_path('app.log'))
        file_handler.setLevel(logging.ERROR)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        logging.getLogger('').addHandler(file_handler)

        logging.config.dictConfig({
            'version': 1,
            'disable_existing_loggers': True,
        })

    def register_endpoints(self):
        @self.server.get("/")
        def home():
            return "Success connected to server!"

        self.server.include_router(self.router)
