import os
import google.generativeai as genai
from google.generativeai import GenerationConfig
from ..Model import GenerativeModel

class Gemini(GenerativeModel):
    def __init__(self):
        google_api_key = os.environ.get("GOOGLE_API_KEY")
        self.model_name = "gemini-pro"
        self.generation_config = GenerationConfig(temperature=0.9,
                                                  top_k=1,
                                                  top_p=1,
                                                  max_output_tokens=2048)
        self.model = None

        genai.configure(api_key=google_api_key)
        self._setup_model()
    
    def _setup_model(self):
        self.model = genai.GenerativeModel(model_name=self.model_name,
                              generation_config=self.generation_config)

    async def generate_text(self, prompt: str|list) -> str:
        """Generates text using the Google Gemini model with error handling.

        Args:
            prompt (str): The text prompt for generation.

        Returns:
            str: The generated text, or an empty string if an error occurred.

        Raises:
            genai.APIError: If an error occurs with the Google API.
        """

        try:
            response = self.model.generate_content(
                contents=prompt
            )
            return response.text
        except Exception as e:
            error_message = f"Error generating text with Gemini: {e}"
            # Log or handle the error appropriately here
            return "Error generating text"