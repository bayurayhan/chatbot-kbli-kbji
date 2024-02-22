import logging
from chatbot.Application import Application
from chatbot.TelegramBot import TelegramBot
from dotenv import load_dotenv
from fastapi import FastAPI
from chatbot.utils import get_path
import os
import sys
print(sys.getdefaultencoding())  # Check default encoding

Application.configure_logging()
logger = logging.getLogger("app")

load_dotenv()
logger.info(".env file loaded!")

server = FastAPI()

HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
PORT = int(os.environ.get("SERVER_PORT", 8000))

# Run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    app = Application.get_instance(server)
    logger.info("Starting application in HTTP mode...")
    WORKERS = os.environ.get("WORKERS", None)
    if WORKERS:
        WORKERS = int(WORKERS)
    uvicorn.run("main:server", host=HOST, port=PORT, workers=WORKERS)
