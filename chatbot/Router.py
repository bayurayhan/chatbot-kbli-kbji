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
from .utils import *
import sys
from .templates import prompt_templates

logger = logging.getLogger("app")


class Router(APIRouter):
    def __init__(
        self,
        telegram_bot: TelegramBot,
        text_generator: TextGeneration,
        intent_classifier: IntentClassifier,
        semantic_search: SemanticSearch,
    ):
        super().__init__(prefix="/api")
        self.bot = telegram_bot
        self.text_generator = text_generator
        self.intent_classifier = intent_classifier
        self.semantic_search = semantic_search

        self.add_api_route(
            "/webhook", self.handleWebhook, methods=["POST"]
        )  # http://localhost:8000/api/webhook

    async def handleWebhook(self, request: Request):
        body = await request.json()

        logger.info(
            f"Chat delivered with id {body.get('update_id')} from {body.get('message', {}).get('from').get('first_name')}"
        )
        logger.debug(body)

        if "message" not in body:
            return
        chat_id = body["message"]["chat"]["id"]
        text = body["message"]["text"]

        save_chat_history(chat_id, "user", text)
        
        await self.bot.to(chat_id).send_action(TelegramAction.TYPING)
        history = read_chat_history(chat_id, 2)
        # history = "\n".join(history)
        prediction = await self.intent_classifier.predict(history)
        intent = prediction["intent"]
        logger.debug(prediction)

        # Handle the intent
        if intent == Intent.MENCARI_KODE:
            await self.handleCariKode(prediction, chat_id, text)
        elif intent == Intent.MENJELASKAN_KODE:
            await self.handleJelaskanKode(prediction, chat_id, text)
        elif intent == Intent.TIDAK_RELEVAN:
            logger.info("Handle `tidak relevan`...")
            await self.bot.to(chat_id).send_action(TelegramAction.TYPING)
            answer = await self.text_generator.generate(
                prompt_templates.for_tidak_relevan(text, chat_id),
                generation_config={"temperature": 0.5},
            )
            await self.bot.to(chat_id).send_text(answer)
        else:
            await self.bot.to(chat_id).send_text("Maaf, terjadi error di sistem!")
            

    async def handleCariKode(self, prediction: dict, chat_id: str, text: str):
        """
        Handling mencari kode intent from intent classification above.

        Args:
            prediction (dict): _description_
            chat_id (str): _description_
            text (str): _description_
        """
        logger.info("Handle `mencari kode`...")

        info_message = await self.bot.to(chat_id).send_text("Mencari informasi...", set_history=False)
        info_message = info_message.get("result")

        query = prediction["entity"]
        dataname = (
            "kbli2020"
            if prediction.get("jenis") == "KBLI"
            else ("kbji2014" if prediction.get("jenis") == "KBJI" else "")
        )
        try:
            digit = int(prediction["digit"])
        except Exception as e:
            digit = None

        raw_response, _ = await self.semantic_search.embedding_query_to_text(
            query, digit, data_name=dataname
        )
        response = ""

        for doc in raw_response:
            response += doc + "\n"

        await self.bot.to(chat_id).send_action(TelegramAction.TYPING)
        answer = await self.text_generator.generate(
            prompt_templates.for_mencari_kode(response, text, dataname, query, chat_id)
        )

        logger.debug(f"Text: {text}, type: {dataname}, {digit}")
        # logger.debug(f"Processed: {preprocessed_query}")
        logger.debug(response)
        logger.debug(answer)

        await self.bot.to(chat_id).send_action(TelegramAction.TYPING)
        await self.bot.to(chat_id).send_text(answer)
        await self.bot.to(chat_id).delete_message(info_message.get("message_id"))

    async def handleJelaskanKode(self, prediction: dict, chat_id: str, text: str):
        """
        Handling menjelaskan kode intent from intent classification above.

        Args:
            prediction (dict): _description_
            chat_id (str): _description_
            text (str): _description_
        """
        logger.info("Handle `menjelaskan kode`...")

        info_message = await self.bot.to(chat_id).send_text("Mencari informasi...", set_history=False)
        info_message = info_message.get("result")

        query = prediction["entity"]
        dataname = (
            "kbli2020"
            if prediction.get("jenis") == "KBLI"
            else ("kbji2014" if prediction.get("jenis") == "KBJI" else "")
        )
        try:
            digit = int(prediction["digit"])
        except Exception as e:
            digit = None

        raw_response, _ = await self.semantic_search.embedding_query_to_text(
            query, digit, data_name=dataname, intent=Intent.MENJELASKAN_KODE
        )
        response = ""

        for doc in raw_response:
            response += doc + "\n"

        await self.bot.to(chat_id).send_action(TelegramAction.TYPING)
        answer = await self.text_generator.generate(
            prompt_templates.for_menjelaskan_kode(response, text, dataname, query, chat_id)
        )

        logger.debug(f"Text: {text}, type: {dataname}, {digit}")
        logger.debug(response)
        logger.debug(answer)

        await self.bot.to(chat_id).send_action(TelegramAction.TYPING)
        await self.bot.to(chat_id).send_text(answer)
        await self.bot.to(chat_id).delete_message(info_message.get("message_id"))
