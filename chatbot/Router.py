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
        body = await request.json()

        logger.info(f"Chat delivered with id {body.get('update_id')} from {body.get('message', {}).get('from').get('first_name')}")
        logger.debug(body)

        if "message" not in body:
            return
        chat_id = body["message"]["chat"]["id"]
        text = body["message"]["text"]

        await self.bot.to(chat_id).send_action(TelegramAction.TYPING)
        prediction = await self.intent_classifier.predict(text)

        # Handle the intent
        if prediction["intent"] == Intent.MENCARI_KODE:
            await self.handleMencariKode(prediction, chat_id, text)
        elif prediction["intent"] == "error":
            await self.bot.to(chat_id).send_text("Error on generating text")
        else:
            await self.bot.to(chat_id).send_action(TelegramAction.TYPING)
            answer = await self.text_generator.generate(f"""system: Anda adalah chatbot yang interaktif dan menyenangkan. Tugas Anda adalah untuk memberi informasi terkait KBLI (Klasifikasi Baku Lapangan Usaha Indonesia) dan KBJI (Klasifikasi Baku Jabatan Indonesia)
Jawab permintaan dari user dengan baik dan sopan.
JANGAN MEMBERI JAWABAN JIKA PERTANYAAN DI LUAR KONTEKS KBLI DAN KBJI!
---
user: {text}
assistant: """)
            await self.bot.to(chat_id).send_text(answer)
            
        return ""
    
    async def handleMencariKode(self, prediction: dict, chat_id: str, text: str):
        """
        Handling mencari kode intent from intent classification above.

        Args:
            prediction (dict): _description_
            chat_id (str): _description_
            text (str): _description_
        """
        logger.info("Handle `mencari kode`...")
        query = prediction["entity"] 
        dataname = "kbli2020" if prediction.get("jenis") == "KBLI" else ("kbji2014" if prediction.get("jenis") == "KBJI" else "")
        try:
            digit = int(prediction["digit"])
        except Exception as e:
            digit = None
         
        raw_response = await self.semantic_search.embedding_query_to_text(query, digit, data_name=dataname)
        response = ""

        for doc in raw_response:
            response += doc + '\n'    

        answer = await self.text_generator.generate(prompt_templates.for_mencari_kode(response, text, dataname, query))
        
        logger.debug(f"Text: {text}, type: {dataname}, {digit}")
        # logger.debug(f"Processed: {preprocessed_query}")
        logger.debug(response)
        logger.debug(answer)

        await self.bot.to(chat_id).send_action(TelegramAction.TYPING)
        await self.bot.to(chat_id).send_text(answer)
