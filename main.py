import logging
from chatbot.Router import Router
from chatbot.utils import *
from chatbot.Application import Application
from chatbot.TelegramBot import TelegramBot
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from chatbot.utils import get_path
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
import time
import os
import sys
from fastapi_events.middleware import EventHandlerASGIMiddleware
from fastapi_events.handlers.local import local_handler
from chatbot.event_handlers import MainEvent, FeedbackEvent

Application.configure_logging()
logger = logging.getLogger("app")

load_dotenv(override=True)
logger.info(".env file loaded!")

server = FastAPI()
app = Application.get_instance()
router = Router(
    telegram_bot=app.telegram_bot,
    intent_classifier=app.intent_classifier,
    text_generator=app.text_generator,
    semantic_search=app.semantic_search,
)

# Register event handler
server.add_middleware(EventHandlerASGIMiddleware, handlers=[local_handler])


@server.get("/")
async def home():
    return "Successfully connected to server!"


# Mount a directory containing the client-side HTML file
server.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

LOG_FILE_PATH = get_path("app.log")
ERROR_FILE_PATH = get_path("err.log")
MAX_LINES = 700


@server.get("/3gVSFXgCqguc3PgHfSfJT2DfEp5Px0", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@server.get("/3gVSFXgCqguc3PgHfSfJT2DfEp5Px0/error", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("error.html", {"request": request})

@server.get("/3gVSFXgCqguc3PgHfSfJT2DfEp5Px0/logs", response_class=HTMLResponse)
async def get_logs():
    with open(LOG_FILE_PATH, "r") as file:
        # Read the last MAX_LINES lines
        lines = file.readlines()[-MAX_LINES:]
        # Reverse the order of lines to show newest lines at the top
        logs = "".join(lines)
    return f"<pre>{logs}</pre>"

@server.get("/3gVSFXgCqguc3PgHfSfJT2DfEp5Px0/logs/error", response_class=HTMLResponse)
async def get_error_logs():
    with open(ERROR_FILE_PATH, "r") as file:
        # Read the last MAX_LINES lines
        lines = file.readlines()[-MAX_LINES:]
        # Reverse the order of lines to show newest lines at the top
        logs = "".join(lines)
    return f"<pre>{logs}</pre>"

server.include_router(router)

HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
PORT = int(os.environ.get("SERVER_PORT", 8000))

# Run the FastAPI server
if __name__ == "__main__":
    import uvicorn

    logger.info("Starting application in HTTP mode...")
    for route in server.routes:
        logger.debug(route)
    WORKERS = os.environ.get("WORKERS", None)
    if WORKERS:
        WORKERS = int(WORKERS)
    uvicorn.run(server, host=HOST, port=PORT, workers=WORKERS)
