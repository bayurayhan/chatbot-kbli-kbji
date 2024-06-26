import asyncio
import logging
import time
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
from fastapi import BackgroundTasks

from fastapi_events.dispatcher import dispatch

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

        self.add_api_route("/webhook", self.handleWebhook, methods=["POST"])  # http://localhost:8000/api/webhook

    async def handleWebhook(self, request: Request, background_task: BackgroundTasks):
        start_time = time.time()
        try:
            body = await request.json()

            logger.debug(body)

            if "callback_query" in body:
                logger.info(
                    f"Callback query delivered from {body.get('callback_query', {}).get('from').get('first_name')}"
                )
                # The update contains a callback query
                callback_query = body["callback_query"]
                user_id = callback_query["from"]["id"]
                response = callback_query[
                    "data"
                ]  # This is the 'callback_data' you set when creating the inline keyboard

                dispatch(
                    "feedback/success",
                    {"is_relevant": response, "user_id": user_id, "poll_id": callback_query["message"]["message_id"]},
                )

                # Now you can handle the callback query
                original_message_id = callback_query["message"]["message_id"]
                chat_id = callback_query["message"]["chat"]["id"]
                self.bot.edit_message_sync(chat_id, original_message_id, "Thank you for your feedback!")

                return

            if ("message" not in body) and ("text" not in body["message"]):
                return

            logger.info(f"Text delivered from {body.get('message', {}).get('from').get('first_name')}")

            chat_id = body["message"]["chat"]["id"]
            text = body["message"]["text"]
            message_id = body["message"]["message_id"]

            if text == "/clearhistory":
                try:
                    os.remove(get_path("chatbot", "history", f"{chat_id}.csv"))
                except:
                    pass

                self.bot.send_text_sync("History telah dihapus!", to=chat_id, set_history=False)
                return
            elif text == "/start":
                self.bot.send_action_sync(chat_id, TelegramAction.TYPING)
                self.bot.send_text_sync(prompt_templates.START_INSTRUCTION, to=chat_id, set_history=False)
                return

            save_chat_history(chat_id, "user", text)

            task = background_task.add_task(self.handleProcess, chat_id, text, message_id, {"start_time": start_time})

            return ""
        except Exception as e:
            logger.error(e)

    def handleProcess(self, chat_id, text, message_id, debug: dict):
        # ===========================================================================
        self.bot.send_action_sync(chat_id, TelegramAction.TYPING)
        history = read_chat_history(chat_id, use_dict=True, n=5)
        history = "\n".join([f'{data["role"]}: <MSG>{data["content"]}</MSG>' for data in history])
        prediction = self.intent_classifier.predict(history)
        intent = prediction["intent"]
        logger.debug(prediction)

        # Handle the intent
        if intent == Intent.MENCARI_KODE:
            self.handleCariKode(prediction, chat_id, text, message_id, {"start_time": debug['start_time']})
        elif intent == Intent.MENJELASKAN_KODE:
            self.handleJelaskanKode(prediction, chat_id, text, message_id, {"start_time": debug['start_time']})
        elif intent == Intent.TIDAK_RELEVAN:
            logger.info("Handle `tidak relevan`...")

            type = prediction["jenis"] if not prediction["jenis"] == "null" else ""
            informations = self.semantic_search.information_retrieval(text, type)

            if informations != "":
                info_message = self.bot.send_text_sync("Mencari informasi dari database...", to=chat_id, set_history=False)
                info_message = info_message.get("result")

            self.bot.send_action_sync(chat_id, TelegramAction.TYPING)
            answer = self.text_generator.generate(
                prompt_templates.for_tidak_relevan(text, chat_id, informations),
                generation_config={"temperature": 0.5},
            )

            answer_message = self.bot.send_text_sync(answer, to=chat_id, reply=message_id)
            answer_message = answer_message.get("result")

            if informations != "":
                self.bot.to(chat_id).delete_message(info_message.get("message_id"))

            dispatch(
                "queryHandled/success",
                {
                    "id": f"{chat_id}__{answer_message.get('message_id')}",
                    "response": answer,
                    "user_prompt": text,
                    "start_time": debug["start_time"],
                },
            )
        else:
            answer_message = self.bot.send_text_sync("Maaf, terjadi error di sistem!", to=chat_id, set_history=False)

            dispatch(
                "queryHandled/success",
                {
                    "id": f"{chat_id}__{answer_message.get('message_id')}",
                    "response": answer,
                    "user_prompt": text,
                    "start_time": debug["start_time"],
                },
            )

        dispatch("queryHandled/all")

    def handleCariKode(self, prediction: dict, chat_id: str, text: str, message_id, debug):
        """
        Handling mencari kode intent from intent classification above.

        Args:
            prediction (dict): _description_
            chat_id (str): _description_
            text (str): _description_
        """
        logger.info("Handle `mencari kode`...")

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

        info_message = self.bot.send_text_sync(
            f"Sedang mencari kode {dataname} untuk {query}...", to=chat_id, set_history=False
        )
        info_message = info_message.get("result")

        # Semantic Search
        raw_response, _ = self.semantic_search.semantic_search(query, digit, data_name=dataname)
        response = ""

        for doc in raw_response:
            response += doc + "\n"

        # Generate answer
        self.bot.send_action_sync(chat_id, TelegramAction.TYPING)
        answer = self.text_generator.generate(
            prompt_templates.for_mencari_kode(response, text, dataname, query, chat_id)
        )

        logger.debug(f"Text: {text}, type: {dataname}, {digit}")
        logger.debug(response)
        logger.debug(answer)

        self.bot.send_action_sync(chat_id, TelegramAction.TYPING)
        answer_message = self.bot.send_text_sync(answer, to=chat_id, reply=message_id)
        answer_message = answer_message.get("result")
        self.bot.to(chat_id).delete_message(info_message.get("message_id"))
        dispatch(
            "queryHandled/success",
            {
                "id": f"{chat_id}__{answer_message.get('message_id')}",
                "response": answer,
                "user_prompt": text,
                "start_time": debug["start_time"],
            },
        )
        dispatch("queryHandled/success/cariKode")

    def handleJelaskanKode(self, prediction: dict, chat_id: str, text: str, message_id, debug):
        """
        Handling menjelaskan kode intent from intent classification above.

        Args:
            prediction (dict): _description_
            chat_id (str): _description_
            text (str): _description_
        """
        logger.info("Handle `menjelaskan kode`...")

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

        info_message = self.bot.send_text_sync(
            f"Mencari penjelasan kode {query} di database...", set_history=False, to=chat_id
        )
        info_message = info_message.get("result")

        raw_response, _ = self.semantic_search.semantic_search(
            query, digit, data_name=dataname, intent=Intent.MENJELASKAN_KODE
        )
        response = ""

        for doc in raw_response:
            response += doc + "\n"

        self.bot.send_action_sync(chat_id, TelegramAction.TYPING)
        answer = self.text_generator.generate(
            prompt_templates.for_menjelaskan_kode(response, text, dataname, query, chat_id)
        )

        logger.debug(f"Text: {text}, type: {dataname}, {digit}")
        logger.debug(response)
        logger.debug(answer)

        self.bot.send_action_sync(chat_id, TelegramAction.TYPING)
        answer_message = self.bot.send_text_sync(answer, to=chat_id, reply=message_id)
        answer_message = answer_message.get("result")
        self.bot.to(chat_id).delete_message(info_message.get("message_id"))
        dispatch(
            "queryHandled/success",
            {
                "id": f"{chat_id}__{answer_message.get('message_id')}",
                "response": answer,
                "user_prompt": text,
                "start_time": debug["start_time"],
            },
        )
        dispatch("queryHandled/success/menjelaskanKode")
