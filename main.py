import logging
from chatbot.Application import Application
from chatbot.TelegramBot import TelegramBot
from dotenv import load_dotenv
from fastapi import FastAPI
import os

Application.configure_logging()
logger = logging.getLogger("app")

load_dotenv()
logger.info(".env file loaded!")

server = FastAPI()
app = Application(server)

HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
PORT = int(os.environ.get("SERVER_PORT", 8000))

# Run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    SSL_CERT = os.environ.get("SSL_CERT")
    SSL_KEY = os.environ.get("SSL_KEY")
    DEBUG = os.environ.get("DEBUG")
    if SSL_CERT and SSL_KEY:
        logger.info("Starting application in HTTP mode...")
        uvicorn.run("main:server", host=HOST, port=PORT, reload=(DEBUG == "true"))
    else:
        logger.info("Starting application in HTTPS mode...")
        uvicorn.run("main:server", host=HOST, port=PORT, reload=(DEBUG == "true"), ssl_certfile=SSL_CERT, ssl_keyfile=SSL_KEY)
