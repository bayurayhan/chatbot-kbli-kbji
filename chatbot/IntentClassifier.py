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
    TIDAK_RELEVAN = "lainnya"

    @classmethod
    def find(cls, value):
        for member in cls:
            if member.value == value:
                return member
        return Intent.TIDAK_RELEVAN

class IntentClassifier:
    def __init__(self, model: GenerativeModel, config: dict):
        self.model = model
        self.config_dict = config["intent-classifier"]

        self.template = self._load_template("intent-prompt-examples.csv")
        # self.only_intent_template = self._load_template("only-intent-prompt-examples.csv")

    def _load_template(self, filename):
        examples_file_path = get_path(
            "chatbot", "templates", filename
        )
        template = []
        with open(examples_file_path, "r", newline="") as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=";")
            header = next(csv_reader)

            for row in csv_reader:
                example_input = {"role": "user", "content": row[0]}
                example_output = {"role": "assistant", "content": row[1]}

                template.append(example_input)
                template.append(example_output)

        return template
        
    def _prepare_for_predict(self, prompt, examples):
        if isinstance(prompt, list):
            system = {'role': 'system', "content": "Chat setelah ini adalah HISTORY chat user!"}
            additional = [system] + prompt
        else:
            additional = [{"role": "user", "content": prompt}]
        file_content = prompt_templates.intent_classification()
        prompt_template = [file_content] + examples + additional
        return prompt_template
    
    # async def fix_query(self, prompt):
    #     generated_template = prompt_templates.prompt_fixer("\n---\n".join([data["content"] for data in prompt]))
    #     fixed_query = await self.model.generate_text(generated_template)
    #     print(fixed_query)
    #     return fixed_query

    async def predict(self, prompt: str):
        # prompt = await self.fix_query(prompt)
        # prompt = " ".join(prompt.split(sep=":")[1:])
        full_prompt = self._prepare_for_predict(prompt, self.template)
        logging.debug(full_prompt)
        prediction = await self.model.generate_text(
            full_prompt,
            self.config_dict["model_config"],
        )
        try:
            logging.debug(prediction)
            prediction = prediction.split(sep=";")
            prediction_dict = {
                "intent": Intent.find(prediction[0]),
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

    # async def predict_only_intent(self, prompt: str):
    #     full_prompt = self._prepare_for_predict(prompt, self.only_intent_template)
    #     prediction = await self.model.generate_text(
    #         full_prompt,
    #         self.config_dict["model_config"],
    #     )
    #     try:
    #         logging.debug(prediction)
    #         return Intent.find(prediction)
    #     except Exception as e:
    #         logging.error(e)
    #         return "error"