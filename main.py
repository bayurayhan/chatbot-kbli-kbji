import logging
from chatbot.Router import Router
from chatbot.Application import Application
from chatbot.TelegramBot import TelegramBot
from dotenv import load_dotenv
from fastapi import FastAPI
from chatbot.utils import get_path
import os
import sys

Application.configure_logging()
logger = logging.getLogger("app")

load_dotenv()
logger.info(".env file loaded!")

server = FastAPI()
app = Application.get_instance()
router = Router(
    telegram_bot=app.telegram_bot,
    intent_classifier=app.intent_classifier,
    text_generator=app.text_generator,
    semantic_search=app.semantic_search,
)
@server.get("/")
async def home():
    return "Successfully connected to server!"

server.include_router(router)

HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
PORT = int(os.environ.get("SERVER_PORT", 8000))

# Run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting application in HTTP mode...")
    for route in server.routes:
        print(route)
    WORKERS = os.environ.get("WORKERS", None)
    if WORKERS:
        WORKERS = int(WORKERS)
    uvicorn.run(server, host=HOST, port=PORT, workers=WORKERS)
