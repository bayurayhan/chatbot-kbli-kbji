import logging
import os
import google.generativeai as genai
from google.generativeai import GenerationConfig
from ..Model import GenerativeModel

logger = logging.getLogger("app")

SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
]


class Gemini(GenerativeModel):
    def __init__(self, generation_config: GenerationConfig = None):
        google_api_key = os.environ.get("GOOGLE_API_KEY")
        self.model_name = "gemini-1.0-pro"
        if not generation_config:
            self.generation_config = GenerationConfig(
                temperature=0, top_k=2, top_p=0.9, max_output_tokens=2048
            )
        else:
            self.generation_config = generation_config
        self.model = None

        genai.configure(api_key=google_api_key)
        self._setup_model()

    def _setup_model(self):
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config,
            safety_settings=SAFETY_SETTINGS,
        )

    async def generate_text(self, prompt: any, generation_config: dict = None) -> str:
        """Generates text using the Google Gemini model with error handling.

        Args:
            prompt (str): The text prompt for generation.

        Returns:
            str: The generated text, or an empty string if an error occurred.

        Raises:
            genai.APIError: If an error occurs with the Google API.
        """
        generation_config = (
            self.generation_config
            if not generation_config
            else GenerationConfig(**generation_config)
        )
        try:
            response = self.model.generate_content(
                prompt, generation_config=generation_config
            )
            return response.text
        except Exception as e:
            error_message = f"Error generating text with Gemini: {e}"
            # Log or handle the error appropriately here
            logger.error(error_message)
            return "Maaf, saya tidak bisa menjawab permintaan Anda."
