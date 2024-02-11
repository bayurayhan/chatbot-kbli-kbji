import fastapi
from .TelegramBot import TelegramBot
from .Router import Router
from .models.Gemini import Gemini
from .models.OpenAIEmbedding import OpenAIEmbedding
from .Model import EmbeddingModel, GenerativeModel
from .IntentClassifier import IntentClassifier
from .TextGeneration import TextGeneration
from .SemanticSearch import SemanticSearch
import logging
import logging.config
from logging.handlers import RotatingFileHandler
from .utils import get_path


class Application:
    def __init__(self, server: fastapi.FastAPI):
        self.server = server

        generative_model: GenerativeModel = Gemini()  # We can edit the model here
        embedding_model: EmbeddingModel = OpenAIEmbedding()

        intent_classifier = IntentClassifier(model=generative_model)
        text_generator = TextGeneration(model=generative_model)
        semantic_search = SemanticSearch(embedding_model=embedding_model)

        self.router = Router(
            telegram_bot=TelegramBot(),
            intent_classifier=intent_classifier,
            text_generator=text_generator,
        )
        self.register_endpoints()

        print("LOADED")

    @staticmethod
    def configure_logging():
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)  # Set root logger level to DEBUG
        # Create a RotatingFileHandler for the root logger with a maximum file size of 1 MB
        root_file_handler = RotatingFileHandler('root.log', maxBytes=1e6, backupCount=3)
        root_file_handler.setLevel(logging.DEBUG)  # Set file handler level to DEBUG
        root_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        root_file_handler.setFormatter(root_formatter)
        root_logger.addHandler(root_file_handler)

        # Create a logger for the application
        app_logger = logging.getLogger('app')
        app_logger.setLevel(logging.DEBUG)  # Set app logger level to DEBUG
        app_file_handler = logging.FileHandler('app.log')
        app_file_handler.setLevel(logging.DEBUG)  # Set file handler level to DEBUG
        app_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        app_file_handler.setFormatter(app_formatter)
        app_logger.addHandler(app_file_handler)

        app_stream_handler = logging.StreamHandler()
        app_stream_handler.setLevel(logging.INFO)  # Set stream handler level to INFO
        app_stream_formatter = logging.Formatter('%(levelname)s - %(message)s')
        app_stream_handler.setFormatter(app_stream_formatter)
        app_logger.addHandler(app_stream_handler)

    def register_endpoints(self):
        @self.server.get("/")
        def home():
            return "Success connected to server!"

        self.server.include_router(self.router)
