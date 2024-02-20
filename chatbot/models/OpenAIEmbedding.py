import os
from langchain_openai import OpenAIEmbeddings as LangChainOpenAIEmbeddings
from ..Model import EmbeddingModel
from tenacity import retry, wait_random_exponential, stop_after_attempt


class OpenAIEmbedding(EmbeddingModel):
    def __init__(self, name="text-embedding-3-large"):
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if api_key == "":
            raise RuntimeError("Please fill OPENAI_API_KEY in .env file!")

        self.embedding_model_name = name
        self.model = LangChainOpenAIEmbeddings(model=self.embedding_model_name)
    
    async def get_embedding(self, documents: any) -> list:
        if isinstance(documents, list):
            embeddings = self.model.embed_documents(documents)
            return embeddings

    def get_model(self):
        return self.model