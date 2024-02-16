import os
from urllib.parse import urljoin
import requests
from typing_extensions import Self
from enum import Enum
from .utils import escape_characters


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

    def get_url(self, path):
        return urljoin(self.url_path, path)

    def to(self, chat_id: any) -> Self:
        self.chat_id = chat_id
        return self

    async def send_text(self, message: str):
        return await self.send_api_request(
            "POST", "sendMessage", data={"text": message}
        )

    async def send_action(self, action: str):
        return await self.send_api_request(
            "POST", "sendChatAction", data={"action": action}
        )

    async def send_api_request(self, method, name, data):
        res = requests.api.request(
            method, self.get_url(name), data={"chat_id": self.chat_id, "parse_mode": "Markdown", **data}
        )

        if res.status_code == 200:
            return res

        raise res.raise_for_status()
