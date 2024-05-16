import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores.faiss import FAISS
from ..Model import EmbeddingModel

class GeminiEmbedding(EmbeddingModel):
    def __init__(self, name="models/text-embedding-004"):
        api_key = os.environ.get("GOOGLE_API_KEY", "")
        if api_key == "":
            raise RuntimeError("Please fill OPENAI_API_KEY in .env file!")

        self.embedding_model_name = name
        self.model = GoogleGenerativeAIEmbeddings(model=self.embedding_model_name)
    
    def faiss_embedding(self, documents: Document, save_folder: str) -> FAISS:
        db = FAISS.from_documents(
            documents, self.model
        )
        db.save_local(save_folder)
        return db

    def load_faiss_embedding(self, faiss_folder: str) -> FAISS:
        db = FAISS.load_local(faiss_folder, self.model)
        return db

    def get_model(self):
        return self.model