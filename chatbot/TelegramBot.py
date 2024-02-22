import asyncio
import logging
import os
from urllib.parse import urljoin
import requests
from typing_extensions import Self
from enum import Enum
from .utils import remove_trailing_asterisks, escape_characters, gemini_markdown_to_markdown, save_chat_history
import markdown
import sys
import json
import re

PARSE_MODE = "MarkdownV2"

class TelegramAction(str, Enum):
    CHOOSE_STICKER = "choose_sticker"
    FIND_LOCATION = "find_location"
    RECORD_VOICE = "record_voice"
    RECORD_VIDEO = "record_video"
    RECORD_VIDEO_NOTE = "record_video_note"
    TYPING = "typing"
    UPLOAD_VOICE = "upload_voice"
    UPLOAD_DOCUMENT = "upload_document"
    UPLOAD_PHOTO = "upload_photo"
    UPLOAD_VIDEO = "upload_video"
    UPLOAD_VIDEO_NOTE = "upload_video_note"


class TelegramBot:
    def __init__(self):
        self.token = os.environ.get("TELEGRAM_API_KEY")
        self.url_path = f"https://api.telegram.org/bot{self.token}/"

        self.chat_id = None
        self.commands = []

        # NOTE: Set all the commands here
        self.set_command("clearhistory", "Bersihkan history chat sebelumnya. (Dibersihkan di dalam server)")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.set_commands())
    
    def set_command(self, command: str, description: str):
        self.commands.append({"command": command, "description": description})

    async def set_commands(self):
        data = {"commands": json.dumps(self.commands)}
        response = await self.send_api_request("POST", "setMyCommands", data)
        return response

    def get_url(self, path):
        return urljoin(self.url_path, path)

    def to(self, chat_id: any) -> Self:
        self.chat_id = chat_id
        return self

    async def send_text(self, message: str, set_history: bool=True):
        if set_history:
            save_chat_history(self.chat_id, "assistant", message)
        message = gemini_markdown_to_markdown(message)
        # message = markdown.markdown(message)
        logging.getLogger("app").debug(message)
        return await self.send_api_request(
            "POST", "sendMessage", data={"text": message, "parse_mode": PARSE_MODE}
        )
    
    async def edit_message(self, message_id: int, message: str):
        return await self.send_api_request(
            "POST", "editMessageText", data={"text": message, "message_id": message_id, "parse_mode": PARSE_MODE}   
        )

    async def delete_message(self, message_id: int):
        return await self.send_api_request(
            "POST", "deleteMessage", data={"message_id": message_id}   
        )

    async def send_action(self, action: str):
        return await self.send_api_request(
            "POST", "sendChatAction", data={"action": action}
        )

    async def send_api_request(self, method, name, data):
        res = requests.api.request(
            method, self.get_url(name), data={"chat_id": self.chat_id, **data}
        )

        if res.status_code == 200:
            return res.json()
        logging.error(res.text)

        raise res.raise_for_status()
