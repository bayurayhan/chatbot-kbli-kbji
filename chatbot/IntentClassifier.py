from enum import Enum
from .Model import GenerativeModel
from .utils import get_path
import csv
import json

class Intent(str, Enum):
    MENCARI_KODE = "mencari kode"
    MENJELASKAN_KODE = "menjelaskan kode"
    TIDAK_RELEVAN = "tidak relevan"

class IntentClassifier:
    def __init__(self, model: GenerativeModel):
        self.model = model
        self.template = []

        self._load_template()

    def _load_template(self):
        examples_file_path = get_path("chatbot\data\intent-prompt-examples.csv")

        with open(examples_file_path, 'r', newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=";")
            header = next(csv_reader)

            for row in csv_reader:
                example_input = "input: " + row[0]
                example_output = "output: " + row[1]

                self.template.append(example_input)
                self.template.append(example_output)

        template_file_path = get_path("chatbot\data\intent-prompt-template.txt")

        with open(template_file_path, 'r') as template_file:
            file_content = template_file.read()

        self.template = [file_content] + self.template
    
    def _prepare_for_predict(self, prompt: str):
        additional = [
            f"input: {prompt}",
            "output: "
        ]
        prompt_template = self.template + additional
        return prompt_template
                
    async def predict(self, prompt: str):
        full_prompt = self._prepare_for_predict(prompt)
        prediction = await self.model.generate_text(full_prompt)
        json_string = prediction.replace('\\n', '\n').replace('\\"', '"')

        try:
            intent_json = json.loads(json_string)
            return intent_json
        except Exception as e:
            print(e)
            return {'intent': 'tidak relevan', 'entity': 'null', 'jenis': 'error', 'digit': 'null'}
 
