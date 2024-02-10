from abc import ABC, abstractmethod

class GenerativeModel(ABC):
    @abstractmethod
    async def generate_text(self, prompt: str|list) -> str:
        """Generates text based on a given prompt with optional control over length and creativity.

        Args:
            prompt: The initial text or starting point for generation.

        Returns:
            The generated text string.
        """