import os
from enum import Enum
import logging
from .Model import GenerativeModel
from .utils import get_path, read_chat_history
import csv
import json
from .templates import prompt_templates


class Intent(str, Enum):
    MENCARI_KODE = "cari kode"
    MENJELASKAN_KODE = "jelaskan kode"
    TIDAK_RELEVAN = "tidak relevan"


class IntentClassifier:
    def __init__(self, model: GenerativeModel, config: dict):
        self.model = model
        self.template = []
        self.config_dict = config["intent-classifier"]

        self._load_template()

    def _load_template(self):
        examples_file_path = get_path(
            "chatbot", "templates", "intent-prompt-examples.csv"
        )

        with open(examples_file_path, "r", newline="") as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=";")
            header = next(csv_reader)

            for row in csv_reader:
                example_input = {"role": "user", "content": row[0]}
                example_output = {"role": "assistant", "content": row[1]}

                self.template.append(example_input)
                self.template.append(example_output)

        file_content = prompt_templates.intent_classification()
        self.template = [file_content] + self.template

    def _prepare_for_predict(self, prompt: str, use_huggingface_template: bool = False):
        additional = [{"role": "user", "content": prompt}]
        prompt_template = self.template + additional
        return prompt_template

    async def predict(self, prompt: str):
        full_prompt = self._prepare_for_predict(prompt)
        prediction = await self.model.generate_text(
            full_prompt,
            self.config_dict["model_config"],
        )
        try:
            logging.debug(prediction)
            prediction = prediction.split(sep=";")
            prediction_dict = {
                "intent": prediction[0],
                "entity": prediction[1],
                "jenis": prediction[2],
                "digit": prediction[3],
            }

            return prediction_dict
        except Exception as e:
            logging.error(e)
            return {
                "intent": "error",
                "entity": "null",
                "jenis": "error",
                "digit": "null",
            }
