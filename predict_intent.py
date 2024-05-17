import time
import yaml
import csv
from chatbot.models.Gemini import Gemini
from chatbot.utils import *
from chatbot.IntentClassifier import IntentClassifier

config_file = get_path("config.yaml")
with open(config_file, "r") as dataset_file:
    config = yaml.safe_load(dataset_file)
generative_model = Gemini(**config["models"]["generative"]["model_params"])
intent_classification = IntentClassifier(model=generative_model, config=config)

# Open the CSV file
with open("evaluations/intent_classification_dataset.csv", "r") as dataset_file:
    # Create a CSV reader
    reader = csv.DictReader(
        dataset_file, delimiter=",", fieldnames=["id", "prompt", "intent", "entity", "type", "digit"]
    )

    headers = next(reader)

    with open("evaluations/intent_classification_prediction.csv", "w", newline="") as prediction_file:
        writer = csv.DictWriter(prediction_file, fieldnames=["id", "prompt", "intent", "entity", "type", "digit"])
        writer.writeheader()

        for i, row in enumerate(reader):
            prompt = row["prompt"]

            prediction = intent_classification.predict(prompt)
            intent = prediction["intent"].value
            entity = prediction["entity"]
            type = prediction["jenis"]
            digit = prediction["digit"]

            writer.writerow({"id": i + 1, "prompt": prompt, "intent": intent, "entity": entity, "type": type, "digit": digit})

            print(f"Progress: {i} -> {intent}", end="\r")
            # Add delay to avoid rate limit for 4 seconds
            time.sleep(4)

# print(intent_classification.predict("Halo, siapa namamu?"))
