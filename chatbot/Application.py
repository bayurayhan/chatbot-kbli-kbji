import asyncio
import fastapi
from .TelegramBot import TelegramBot
# from .models.Gemini import Gemini
# from .models.OpenAIEmbedding import OpenAIEmbedding
# from .models.GPT4Free import GPT4Free
from .models import *
from .Model import EmbeddingModel, GenerativeModel
from .IntentClassifier import IntentClassifier
from .TextGeneration import TextGeneration
from .SemanticSearch import SemanticSearch
import logging
import logging.config
from logging.handlers import RotatingFileHandler
from .utils import *
import yaml
import sys


logger = logging.getLogger("app")


class Application:
    _instance = None

    def __init__(self):
        if Application._instance is not None:
            raise Exception("Application instance already exists. Use get_instance() to access it.")
        self.config_file = get_path("config.yaml")
        self.config = None
        self.generative_model = None
        self.embedding_model = None
        self.load_configuration()

        self.intent_classifier = IntentClassifier(model=self.generative_model, config=self.config)
        self.text_generator = TextGeneration(model=self.generative_model)
        self.semantic_search = SemanticSearch(
            embedding_model=self.embedding_model, text_generator=self.generative_model, config=self.config
        )
        
        self.telegram_bot = TelegramBot()

    @staticmethod
    def get_instance():
        if Application._instance is None:
            Application._instance = Application()
        return Application._instance

    def load_configuration(self):
        logger.info(f"Load the configuration file from {self.config_file}...")
        with open(self.config_file, 'r') as file:
            self.config = yaml.safe_load(file)

        generative_model_config = self.config['models']['generative']
        embedding_model_config = self.config['models']['embedding']

        generative_model_class = generative_model_config['model_name']
        embedding_model_class = embedding_model_config['model_name']

        # Dynamically import generative model class
        generative_module_name, generative_class_name = generative_model_class.rsplit('.', 1)
        generative_module = __import__(generative_module_name, fromlist=[generative_class_name])
        GenerativeModel = getattr(generative_module, generative_class_name)

        # Dynamically import embedding model class
        embedding_module_name, embedding_class_name = embedding_model_class.rsplit('.', 1)
        embedding_module = __import__(embedding_module_name, fromlist=[embedding_class_name])
        EmbeddingModel = getattr(embedding_module, embedding_class_name)

        self.generative_model = GenerativeModel(**generative_model_config.get('model_params', {}))
        self.embedding_model = EmbeddingModel(**embedding_model_config.get('model_params', {}))

    @staticmethod
    def configure_logging():
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)  # Set root logger level to DEBUG
        # Create a RotatingFileHandler for the root logger with a maximum file size of 1 MB
        root_file_handler = RotatingFileHandler("root.log", maxBytes=1e6, backupCount=3, encoding='utf-8')
        root_file_handler.setLevel(logging.DEBUG)  # Set file handler level to DEBUG
        root_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        root_file_handler.setFormatter(root_formatter)
        root_logger.addHandler(root_file_handler)

        # Create a logger for the application
        app_logger = logging.getLogger("app")
        app_logger.setLevel(logging.DEBUG)  # Set app logger level to DEBUG
        app_file_handler = RotatingFileHandler("app.log", maxBytes=1e6, backupCount=2, encoding='utf-8')
        app_file_handler.setLevel(logging.DEBUG)  # Set file handler level to DEBUG
        app_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        app_file_handler.setFormatter(app_formatter)
        app_logger.addHandler(app_file_handler)

        app_stream_handler = logging.StreamHandler()
        app_stream_handler.setLevel(logging.INFO)  # Set stream handler level to INFO
        app_stream_formatter = logging.Formatter(
            "%(asctime)s %(levelname)s - %(message)s"
        )
        app_stream_handler.setFormatter(app_stream_formatter)
        app_logger.addHandler(app_stream_handler)