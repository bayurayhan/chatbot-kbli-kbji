import logging
import os
import google.generativeai as genai
from google.generativeai import GenerationConfig
from ..Model import GenerativeModel
import traceback

logger = logging.getLogger("app")

SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
]


class Gemini(GenerativeModel):
    def __init__(
        self,
        name="gemini-1.0-pro",
        temperature=0.5,
        top_p=0.5,
        top_k=40,
        max_output_tokens=4000,
    ):
        google_api_key = os.environ.get("GOOGLE_API_KEY")
        self.model_name = name
        self.generation_config = GenerationConfig(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            max_output_tokens=max_output_tokens,
        )
        self.model = None

        genai.configure(api_key=google_api_key)
        self._setup_model()

    def _setup_model(self):
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config,
            safety_settings=SAFETY_SETTINGS,
        )

    def _generate_string(self, prompt: list[dict]) -> list[str]:
        generated_string = []
        for message in prompt:
            generated_string.append(f"{message['role']}: {message['content']}\n")
        generated_string.append(f"assistant: ")
        return generated_string

    async def generate_text(
        self, prompt: list[dict], generation_config: dict = None
    ) -> str:
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
            prompt = self._generate_string(prompt)
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_message = f"Error generating text with Gemini: {e}"
            # Log or handle the error appropriately here
            logger.error(traceback.format_exc())
            return "Maaf, saya tidak bisa menjawab permintaan Anda."
