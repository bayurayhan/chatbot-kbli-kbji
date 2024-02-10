from abc import ABC, abstractmethod

class GenerativeModel(ABC):
    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """Generates text based on a given prompt with optional control over length and creativity.

        Args:
            prompt: The initial text or starting point for generation.

        Returns:
            The generated text string.
        """