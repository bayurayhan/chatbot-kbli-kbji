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
        self.message_id = None
        self.commands = []

        # NOTE: Set all the commands here
        self.set_command("clearhistory", "Bersihkan history chat sebelumnya. (Dibersihkan di dalam server)")
        self.set_commands()
    
    def set_command(self, command: str, description: str):
        self.commands.append({"command": command, "description": description})

    def set_commands(self):
        data = {"commands": json.dumps(self.commands)}
        response =   self.send_api_request("POST", "setMyCommands", data)
        return response

    def get_url(self, path):
        return urljoin(self.url_path, path)

    def to(self, chat_id: any) -> Self:
        self.chat_id = chat_id
        return self

    def reply(self, message_id) -> Self:
        self.message_id = message_id
        return self

    def divide_message(self, message: str, max_length: int = 4087):
        words = message.split(' ')
        chunks = []
        current_chunk = ''
        
        for word in words:
            if len(current_chunk) + len(word) + 1 < max_length:
                current_chunk += ' ' + word
            else:
                # Add "..." to the end of the chunk if it's not the last one
                chunks.append(current_chunk + '\\.\\.\\.')
                current_chunk = word
        
        chunks.append(current_chunk)
        return chunks

    def send_text(self, message: str, set_history: bool=True):
        if set_history:
            save_chat_history(self.chat_id, "assistant", message)
        message = gemini_markdown_to_markdown(message)
        # message = markdown.markdown(message)

        # Divide the message into chunks
        chunks = self.divide_message(message)
        logging.getLogger("app").debug(chunks)

        info_message = None
        
        if self.message_id:
            for i, chunk in enumerate(chunks):
                if i == 0:
                    info_message = self.send_api_request(
                        "POST", "sendMessage", data={"text": chunk, "parse_mode": PARSE_MODE, "reply_to_message_id": self.message_id}
                    )
                else:
                    info_message = self.send_api_request(
                        "POST", "sendMessage", data={"text": chunk, "parse_mode": PARSE_MODE}
                    )
                    
        else:
            for chunk in chunks:
                info_message = self.send_api_request(
                    "POST", "sendMessage", data={"text": chunk, "parse_mode": PARSE_MODE}
                )
        
        self.message_id = None        
        
        return info_message
    
    def edit_message(self, message_id: int, message: str):
        return   self.send_api_request(
            "POST", "editMessageText", data={"text": message, "message_id": message_id, "parse_mode": PARSE_MODE}   
        )

    def delete_message(self, message_id: int):
        return   self.send_api_request(
            "POST", "deleteMessage", data={"message_id": message_id}   
        )

    def send_action(self, action: str):
        return   self.send_api_request(
            "POST", "sendChatAction", data={"action": action}
        )

    def send_api_request(self, method, name, data):
        res = requests.api.request(
            method, self.get_url(name), data={"chat_id": self.chat_id, **data}
        )

        if res.status_code == 200:
            return res.json()
        logging.error(res.text)

        raise res.raise_for_status()
