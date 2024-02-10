import os
import openai
from ..Model import EmbeddingModel


class OpenAIEmbedding(EmbeddingModel):
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if api_key == "":
            raise RuntimeError("Please fill OPENAI_API_KEY in .env file!")

        self.embedding_model = "text-embedding-3-large"
        self.openai_client = openai.OpenAI(api_key=api_key)

    async def get_embedding(self, text: str):
        response = self.openai_client.embeddings.create(input=[text], model=self.embedding_model)
        print(response)
        # return response["embedding"]
