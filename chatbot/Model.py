from abc import ABC, abstractmethod
from langchain_core.documents import Document
from langchain_community.vectorstores.faiss import FAISS

class GenerativeModel(ABC):
    @abstractmethod
    async def generate_text(self, prompt: list[dict], generation_config: dict = None) -> str:
        """Generates text based on a given prompt with optional control over length and creativity.

        Args:
            prompt: The initial text or starting point for generation.

        Returns:
            The generated text string.
        """

class EmbeddingModel(ABC):
    @abstractmethod
    def faiss_embedding(self, documents: Document, save_folder: str) -> FAISS:
        """
        Abstract method to get the embedding of a given text.

        Parameters:
            documents (Langchain Document): The input text for which embedding is required.

        Returns:
            FAISS DB
        """
    @abstractmethod
    def load_faiss_embedding(self, faiss_folder: str) -> FAISS:
        """
        Load FAISS embedding.
        
        Parameters:
            faiss_folder
            
        Returns:
            FAISS DB
        """ 
    
    @abstractmethod
    def get_model(self):
        """
        Get the model object from the source API
        """