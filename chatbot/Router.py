import asyncio
import logging
from fastapi import APIRouter, Request
from urllib.parse import urljoin

from .Application import Application
from .TelegramBot import TelegramBot, TelegramAction
import requests as httpRequest
from .TextGeneration import TextGeneration
from .IntentClassifier import IntentClassifier, Intent
from .SemanticSearch import SemanticSearch
import json
from .utils import *
import sys
from .templates import prompt_templates
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from pathos.multiprocessing import ProcessingPool
from fastapi import BackgroundTasks

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

    def handleProcess(self, chat_id, text):
        # ===========================================================================
        self.bot.to(chat_id).send_action(TelegramAction.TYPING)
        history = read_chat_history(chat_id, 4)
        history = "\n---\n".join([data["content"] for data in history])
        prediction = self.intent_classifier.predict(history)
        intent = prediction["intent"]
        logger.debug(prediction)

        # Handle the intent
        if intent == Intent.MENCARI_KODE:
            self.handleCariKode(prediction, chat_id, text)
        elif intent == Intent.MENJELASKAN_KODE:
            self.handleJelaskanKode(prediction, chat_id, text)
        elif intent == Intent.TIDAK_RELEVAN:
            logger.info("Handle `tidak relevan`...")

            type = prediction["jenis"] if not prediction["jenis"] == "null" else ""
            informations = self.semantic_search.information_retrieval(text, type)

            self.bot.to(chat_id).send_action(TelegramAction.TYPING)
            answer = self.text_generator.generate(
                prompt_templates.for_tidak_relevan(text, chat_id, informations),
                generation_config={"temperature": 0.5},
            )
            self.bot.to(chat_id).send_text(answer)
        else:
            self.bot.to(chat_id).send_text("Maaf, terjadi error di sistem!")

    async def handleWebhook(self, request: Request, background_task: BackgroundTasks):
        body = await request.json()

        logger.info(
            f"Chat delivered with id {body.get('update_id')} from {body.get('message', {}).get('from').get('first_name')}"
        )
        logger.debug(body)

        if "message" not in body:
            return
        chat_id = body["message"]["chat"]["id"]
        text = body["message"]["text"]

        if text == "/clearhistory":
            try:
                os.remove(get_path("chatbot", "history", f"{chat_id}.csv"))
            except:
                pass
                
            self.bot.to(chat_id).send_text("History telah dihapus!", False)
            return

        task = background_task.add_task(self.handleProcess, chat_id, text)
        
        return ""
        

    def handleCariKode(self, prediction: dict, chat_id: str, text: str):
        """
        Handling mencari kode intent from intent classification above.

        Args:
            prediction (dict): _description_
            chat_id (str): _description_
            text (str): _description_
        """
        logger.info("Handle `mencari kode`...")

        info_message =   self.bot.to(chat_id).send_text("Mencari informasi...", set_history=False)
        info_message = info_message.get("result")

        # Extracting query and digit
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

        # Semantic Search
        raw_response, _ =   self.semantic_search.semantic_search(
            query, digit, data_name=dataname
        )
        response = ""

        for doc in raw_response:
            response += doc + "\n"

        # Generate answer
        self.bot.to(chat_id).send_action(TelegramAction.TYPING)
        answer =   self.text_generator.generate(
            prompt_templates.for_mencari_kode(response, text, dataname, query, chat_id)
        )

        logger.debug(f"Text: {text}, type: {dataname}, {digit}")
        logger.debug(response)
        logger.debug(answer)

        self.bot.to(chat_id).send_action(TelegramAction.TYPING)
        self.bot.to(chat_id).send_text(answer)
        self.bot.to(chat_id).delete_message(info_message.get("message_id"))

    def handleJelaskanKode(self, prediction: dict, chat_id: str, text: str):
        """
        Handling menjelaskan kode intent from intent classification above.

        Args:
            prediction (dict): _description_
            chat_id (str): _description_
            text (str): _description_
        """
        logger.info("Handle `menjelaskan kode`...")

        info_message =  self.bot.to(chat_id).send_text("Mencari informasi...", set_history=False)
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

        raw_response, _ =   self.semantic_search.semantic_search(
            query, digit, data_name=dataname, intent=Intent.MENJELASKAN_KODE
        )
        response = ""

        for doc in raw_response:
            response += doc + "\n"

        self.bot.to(chat_id).send_action(TelegramAction.TYPING)
        answer =   self.text_generator.generate(
            prompt_templates.for_menjelaskan_kode(response, text, dataname, query, chat_id)
        )

        logger.debug(f"Text: {text}, type: {dataname}, {digit}")
        logger.debug(response)
        logger.debug(answer)

        self.bot.to(chat_id).send_action(TelegramAction.TYPING)
        self.bot.to(chat_id).send_text(answer)
        self.bot.to(chat_id).delete_message(info_message.get("message_id"))
