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
from .FeedbackSystem import FeedbackSystem
import logging
import logging.config
from logging.handlers import RotatingFileHandler
from .utils import *
import yaml
import sys
import logging

class CustomFormatter(logging.Formatter):

    grey = "\033[90m"
    yellow = "\033[93m"
    red = "\033[91m"
    bold_red = "\033[1;91m"
    reset = "\033[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

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
        self.feedback_system = FeedbackSystem(config=self.config, telegram_bot=self.telegram_bot)

    @staticmethod
    def get_instance():
        if Application._instance is None:
            Application._instance = Application()
        return Application._instance

    def load_configuration(self):
        logger.info(f"Load the configuration file from {self.config_file}...")
        with open(self.config_file, "r") as file:
            self.config = yaml.safe_load(file)

        generative_model_config = self.config["models"]["generative"]
        embedding_model_config = self.config["models"]["embedding"]

        generative_model_class = generative_model_config["model_name"]
        embedding_model_class = embedding_model_config["model_name"]

        # Dynamically import generative model class
        generative_module_name, generative_class_name = generative_model_class.rsplit(".", 1)
        generative_module = __import__(generative_module_name, fromlist=[generative_class_name])
        GenerativeModel = getattr(generative_module, generative_class_name)

        # Dynamically import embedding model class
        embedding_module_name, embedding_class_name = embedding_model_class.rsplit(".", 1)
        embedding_module = __import__(embedding_module_name, fromlist=[embedding_class_name])
        EmbeddingModel = getattr(embedding_module, embedding_class_name)

        self.generative_model = GenerativeModel(**generative_model_config.get("model_params", {}))
        self.embedding_model = EmbeddingModel(**embedding_model_config.get("model_params", {}))

    @staticmethod
    def configure_logging():

        # # Set all loggers inside logging.root.manager.loggerDict to WARNING
        # for logger_name in logging.root.manager.loggerDict:
        #     # add rotating file handler to all loggers
        #     logging.getLogger(logger_name).addHandler(root_file_handler)

        error_handler = RotatingFileHandler("err.log", maxBytes=1e6, backupCount=5, encoding="utf-8")
        error_handler.setLevel(logging.ERROR)  # Only handle errors (WARNING and above)
        error_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)")
        error_handler.setFormatter(error_formatter)

        root_logger = logging.getLogger()
        root_logger.removeHandler(root_logger.handlers[0])
        root_logger.setLevel(logging.NOTSET)  # Set root logger level to DEBUG
        # # Create a RotatingFileHandler for the root logger with a maximum file size of 1 MB
        root_file_handler = RotatingFileHandler("root.log", maxBytes=1e6, backupCount=3, encoding="utf-8")
        root_file_handler.setLevel(logging.NOTSET)  # Set file handler level to DEBUG
        root_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)")
        root_file_handler.setFormatter(root_formatter)
        root_logger.addHandler(root_file_handler)
        root_logger.addHandler(error_handler)

        # Create a logger for the application
        app_logger = logging.getLogger("app")
        app_logger.setLevel(logging.DEBUG)  # Set app logger level to DEBUG
        app_file_handler = RotatingFileHandler("app.log", maxBytes=1e6, backupCount=2, encoding="utf-8")
        app_file_handler.setLevel(logging.DEBUG)  # Set file handler level to DEBUG
        app_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)")
        app_file_handler.setFormatter(app_formatter)
        app_logger.addHandler(app_file_handler)
        app_logger.addHandler(error_handler)

        app_stream_handler = logging.StreamHandler(stream=sys.stdout)
        app_stream_handler.setLevel(logging.INFO)  # Set stream handler level to INFO
        app_stream_handler.addFilter(lambda record: record.levelname == "INFO" or record.levelno >= 40)
        app_stream_handler.setFormatter(CustomFormatter())
        app_logger.addHandler(app_stream_handler)
