import os
import pandas as pd
from .TelegramBot import TelegramBot


class FeedbackSystem:
    _instance = None
    chunksize = 500  # adjust this value depending on your available memory

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(FeedbackSystem, cls).__new__(cls)
        return cls._instance

    def __init__(self, config: dict, telegram_bot: TelegramBot):
        self.config = config["feedback-system"]
        self.telegram_bot = telegram_bot

        self.file_path = self.config["file_path"]
        self.create_file()

    @staticmethod
    def get_instance():
        if FeedbackSystem._instance is None:
            raise RuntimeError("FeedbackSystem must be initiated before!")
        return FeedbackSystem._instance
    
    def send_poll(self, chat_id, message_id):
        keyboard = [[{'text': 'Relevan', 'callback_data': '1'}, {'text': 'Tidak relevan', 'callback_data': '0'}]]
        return self.telegram_bot.to(chat_id).reply(message_id).send_message_with_inline_keyboard("Bagaimana respon dari chatbot?", keyboard)

    def create_file(self):
        if not os.path.exists(self.file_path):
            df = pd.DataFrame(
                columns=[
                    "id",
                    "poll_id"
                    "user_prompt",
                    "response",
                    "response_time",
                    "is_relevant",
                    "is_error",
                ]
            )
            df.to_csv(self.file_path, index=False)

    def add_feedback(self, id, poll_id, user_prompt, response, response_time, is_relevant, is_error):
        df = pd.read_csv(self.file_path)
        new_feedback = pd.DataFrame(
            {
                "id": [id],
                "poll_id": [poll_id],
                "user_prompt": [user_prompt],
                "response": [response],
                "response_time": [response_time],
                "is_relevant": [is_relevant],
                "is_error": [is_error],
            }
        )
        df = pd.concat([df, new_feedback], ignore_index=True)
        df.to_csv(self.file_path, index=False)

    def edit_feedback(self, id, column, new_data):
        if os.path.getsize(self.file_path) > 0:
            chunk_container = pd.read_csv(self.file_path, chunksize=self.chunksize)
            for chunk in chunk_container:
                chunk.loc[chunk["id"] == id, column] = new_data
                chunk.to_csv(self.file_path, mode="a", index=False)
        else:
            print("File is empty.")
