import os
import pandas as pd
from .TelegramBot import TelegramBot
import mysql.connector


class FeedbackSystem:
    _instance = None
    chunksize = 500  # adjust this value depending on your available memory

    def __new__(cls, *args, **kwargs):
        """
        Creates a new instance of FeedbackSystem if it doesn't already exist.

        Args:
            cls: The class.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The instance of FeedbackSystem.
        """
        if not cls._instance:
            cls._instance = super(FeedbackSystem, cls).__new__(cls)
        return cls._instance

    def __init__(self, config: dict, telegram_bot: TelegramBot):
        self.config = config["feedback-system"]
        self.telegram_bot = telegram_bot
        self.db_conn = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),
            user=os.environ.get("MYSQL_USER", "root"),
            password=os.environ.get("MYSQL_PASSWORD", ""),
            database=os.environ.get("MYSQL_DATABASE", "chatbot"),
        )
        self.db_cursor = self.db_conn.cursor()
        self.create_table()

    def create_table(self):
        self.db_cursor.execute(
            """CREATE TABLE IF NOT EXISTS feedback_data (
                                    id INT PRIMARY KEY AUTO_INCREMENT,
                                    unique_id VARCHAR(20),
                                    poll_id INT,
                                    user_prompt TEXT,
                                    response TEXT,
                                    response_time TEXT,
                                    is_relevant INT,
                                    is_error INT
                                  )"""
        )

    @staticmethod
    def get_instance():
        """
        A static method that returns the instance of the FeedbackSystem if it exists, otherwise raises an error.
        """
        if FeedbackSystem._instance is None:
            raise RuntimeError("FeedbackSystem must be initiated before!")
        return FeedbackSystem._instance

    def send_feedback_poll(self, chat_id, message_id):
        """
        Send a poll with a predefined keyboard layout to a specific chat ID and message ID.

        Parameters:
            chat_id: The ID of the chat where the poll will be sent.
            message_id: The ID of the message to which the poll will be a response.

        Returns:
            Response from the Telegram API after sending the poll with the inline keyboard.
        """
        keyboard = [[{"text": "Relevan", "callback_data": 1}, {"text": "Tidak relevan", "callback_data": 0}]]
        return (
            self.telegram_bot.to(chat_id)
            .reply(message_id)
            .send_message_with_inline_keyboard("Bagaimana respon dari chatbot?", keyboard)
        )

    def send_edit_feedback_poll(self, chat_id, message_id):
        """
        Edit a poll with a predefined keyboard layout to a specific chat ID and message ID.

        Parameters:
            chat_id: The ID of the chat where the poll will be sent.
            message_id: The ID of the message to which the poll will be a response.

        Returns:
            Response from the Telegram API after sending the edited message with thank you message.
        """
        return self.telegram_bot.to(chat_id).edit_message(message_id, "Terima kasih!")


    def add_feedback(self, id, poll_id, user_prompt, response, response_time, is_relevant, is_error):
        self.db_cursor.execute(
            """INSERT INTO feedback_data (unique_id, poll_id, user_prompt, response, response_time, is_relevant, is_error)
                                  VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (id, poll_id, user_prompt, response, response_time, is_relevant, is_error),
        )
        self.db_conn.commit()

    def edit_feedback(self, poll_id, column, new_data):
        self.db_cursor.execute(
            """UPDATE feedback_data SET {} = %s WHERE poll_id = %s""".format(column),
            (new_data, poll_id),
        )
        self.db_conn.commit()

    def __del__(self):
        self.db_conn.close()
