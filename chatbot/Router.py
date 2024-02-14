import asyncio
import logging
from fastapi import APIRouter, Request
from urllib.parse import urljoin
from .TelegramBot import TelegramBot, TelegramAction
import requests as httpRequest
from .TextGeneration import TextGeneration
from .IntentClassifier import IntentClassifier, Intent
from .SemanticSearch import SemanticSearch
import json
from .utils import read_specific_row, get_path
from .templates import prompt_templates

logger = logging.getLogger("app")

class Router(APIRouter):
    def __init__(self, telegram_bot: TelegramBot, text_generator: TextGeneration, intent_classifier: IntentClassifier, semantic_search: SemanticSearch):
        super().__init__(prefix="/api")
        self.bot = telegram_bot
        self.text_generator = text_generator
        self.intent_classifier = intent_classifier
        self.semantic_search = semantic_search

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
        try:
            digit = int(prediction["digit"])
        except Exception as e:
            digit = None
        
        raw_response = await self.semantic_search.embedding_query_to_text(query, digit)
        response = ""

        for doc in raw_response:
            response += doc + '\n'    

        answer = await self.text_generator.generate(prompt_templates.for_mencari_kode(response, text, type, query))
        
        logger.info(f"Text: {text}, type: {type}, {digit}")
        # logger.debug(f"Processed: {preprocessed_query}")
        logger.info(response)

        await self.bot.to(chat_id).send_action(TelegramAction.TYPING)
        await self.bot.to(chat_id).send_text(answer)
