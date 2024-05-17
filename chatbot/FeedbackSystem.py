import os
import pandas as pd
from .TelegramBot import TelegramBot


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
        """
        Initializes the FeedbackSystem with the provided configuration and TelegramBot instance.

        Args:
            config (dict): The configuration dictionary containing settings for the feedback system.
            telegram_bot (TelegramBot): An instance of the TelegramBot class to handle Telegram interactions.

        Returns:
            None
        """
        self.config = config["feedback-system"]
        self.telegram_bot = telegram_bot

        self.file_path = self.config["file_path"]
        self.create_file()

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
        keyboard = [[{'text': 'Relevan', 'callback_data': '1'}, {'text': 'Tidak relevan', 'callback_data': '0'}]]
        return self.telegram_bot.to(chat_id).reply(message_id).send_message_with_inline_keyboard("Bagaimana respon dari chatbot?", keyboard)
    
    def edit_feedback_poll(self, chat_id, message_id):
        """
        Edit a poll with a predefined keyboard layout to a specific chat ID and message ID.
        
        Parameters:
            chat_id: The ID of the chat where the poll will be sent.
            message_id: The ID of the message to which the poll will be a response.
        
        Returns:
            Response from the Telegram API after sending the edited message with thank you message.
        """
        return self.telegram_bot.to(chat_id).edit_message(message_id, "Terima kasih!")

    def create_file(self):
        """
        Checks if the file at the specified path exists and creates a DataFrame with the specified columns if it doesn't exist. Then, it saves the DataFrame to a CSV file at the specified path.

        Parameters:
            self: The instance of the class.
        
        Returns:
            None
        """
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
        """
        Adds feedback data to a DataFrame, concatenates it with an existing DataFrame, and saves the combined DataFrame to a CSV file.
        
        Parameters:
            self: The instance of the class.
            id: The ID of the feedback.
            poll_id: The ID of the poll.
            user_prompt: The prompt provided by the user.
            response: The response to the prompt.
            response_time: The time of the response.
            is_relevant: Indicator of relevance.
            is_error: Indicator of error.
        
        Returns:
            None
        """
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
        """
        Edits the feedback data in the file based on the provided ID, column, and new data.

        Parameters:
            self: The instance of the class.
            id: The ID of the feedback.
            column: The column to be edited.
            new_data: The new data to replace the existing data.

        Returns:
            None
        """
        if os.path.getsize(self.file_path) > 0:
            chunk_container = pd.read_csv(self.file_path, chunksize=self.chunksize)
            for chunk in chunk_container:
                chunk.loc[chunk["id"] == id, column] = new_data
                chunk.to_csv(self.file_path, mode="a", index=False)
        else:
            print("File is empty.")
