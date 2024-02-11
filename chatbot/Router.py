import logging
from fastapi import APIRouter, Request
from urllib.parse import urljoin
from .TelegramBot import TelegramBot, TelegramAction
import requests as httpRequest
from .TextGeneration import TextGeneration
from .IntentClassifier import IntentClassifier, Intent
import json


class Router(APIRouter):
    def __init__(self, telegram_bot: TelegramBot, text_generator: TextGeneration, intent_classifier: IntentClassifier ):
        super().__init__(prefix="/api")
        self.bot = telegram_bot
        self.text_generator = text_generator
        self.intent_classifier = intent_classifier

        self.add_api_route("/webhook", self.handleWebhook, methods=["POST"]) # http://localhost:8000/api/webhook

    async def handleWebhook(self, request: Request):
        # TODO: Need to be implemented
        body = await request.json()
        chat_id = body["message"]["chat"]["id"]
        text = body["message"]["text"]

        await self.bot.to(chat_id).send_action(TelegramAction.TYPING)
        prediction = await self.intent_classifier.predict(text)

        # Handle the intent
        if prediction["intent"] == Intent.MENCARI_KODE:
            await self.handleMencariKode(prediction, chat_id, text)

        # generated_response = self.text_generator.generate(text)

        # await self.bot.to(chat_id).send_text(generated_response)
        
        return ""
    
    async def handleMencariKode(self, prediction: dict, chat_id, text):
        query = prediction["entity"]
        type = prediction["jenis"]
        digit = prediction["digit"]

        response = await self.text_generator.generate(f"""Informasikan ke user bahwa kamu (Chatbot) sedang mencari kode yang dimaksudkan user di database.
user: {text}
chatbot: """)

        await self.bot.to(chat_id).send_text(response)
