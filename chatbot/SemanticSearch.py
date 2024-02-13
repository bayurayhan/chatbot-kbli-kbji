import logging
from .utils import get_path
import os
from .Model import EmbeddingModel
import numpy as np
import pandas as pd
from tqdm.auto import tqdm
import asyncio
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores.faiss import FAISS
from langchain.text_splitter import TokenTextSplitter, CharacterTextSplitter

logger = logging.getLogger("app")


class SemanticSearch:
    def __init__(self, embedding_model: EmbeddingModel):
        self.db_path = get_path(os.path.join("chatbot", "data", "baku.db"))
        self.embedding_model = embedding_model

        embedded_file_path = get_path(os.path.join("chatbot", "data", ".EMBEDDED"))
        if not os.path.exists(embedded_file_path):
            logger.info(
                "Creating embedding for the database. This may take some time..."
            )
            self._embed_database()
            self._create_embedded_file(embedded_file_path)

        # FIXME: Test
        db = self._load_embedding_data("kbli2020")
        print(db.similarity_search("tukang bangunan"))


    def _embed_database(self):
        asyncio.run(self._process_embedding("kbli2020"))
        # asyncio.run(self._process_embedding("kbji2014"))

    async def _process_embedding(self, data_name: str):
        try:
            embedded_file_path = get_path(
                os.path.join("chatbot", "data", f"{data_name}_embedding.csv")
            )
            if os.path.exists(embedded_file_path):
                logger.info(f"Skipping {data_name} embedding.")
                return

            column_types = {"kode": "str"}

            df = pd.read_csv(
                get_path(os.path.join("chatbot", "data", f"{data_name}.csv")),
                dtype=column_types,
            )

            df["deskripsi"] = df["deskripsi"].fillna("unknown")

            df["judul_deskripsi"] = df["judul"] + "\n" + df["deskripsi"]
            # df["judul_deskripsi_embedding"] = await self.embedding_model.get_embedding(
            #     df["judul_deskripsi"].to_list()
            # )

            # del df["judul_deskripsi"]
            df = df["judul"]
            df.to_csv(
                get_path(os.path.join("chatbot", "data", f"{data_name}_embedding.csv")),
                index=False,
            )
            logger.info(f"Successfully generating embbeding for {data_name}")

        except Exception as e:
            logger.error(e)
            raise RuntimeError(
                "Error when embedding the database, please check the log file."
            )

    def _load_embedding_data(self, data_name=None) -> FAISS:
        """
        Loading the csv file that containing all data that already been
        embedded. If the file is not already existed, do embed_dataset function.

        Args:
            csv_file_path (str): file path for csv data

        Return:
            Numpy array of the loaded embedding
        """
        faiss_folder = os.path.join("chatbot", "data", f"{data_name}_faiss_index")

        if not os.path.exists(faiss_folder):
            logger.info("Load the documents...")
            loader = CSVLoader(
                get_path(os.path.join("chatbot", "data", f"{data_name}_embedding.csv")),
            )
            documents = loader.load()

            # # Load to FAISS database
            db = FAISS.from_documents(documents, self.embedding_model.get_model())
            db.save_local(
                get_path(os.path.join("chatbot", "data", f"{data_name}_faiss_index"))
            )
            return db
        
        db = FAISS.load_local(faiss_folder, self.embedding_model.get_model())
        return db
        
    @staticmethod
    def cosine_similarity(embedding1: list, embedding2: list) -> float:
        """
        Calculate the cosine similarity between two embeddings.

        Parameters:
            embedding1 (list): The first embedding.
            embedding2 (list): The second embedding.

        Returns:
            float: The cosine similarity score between the two embeddings.
        """
        embedding1 = np.array(embedding1)
        embedding2 = np.array(embedding2)
        dot_product = np.dot(embedding1, embedding2)
        magnitude1 = np.linalg.norm(embedding1)
        magnitude2 = np.linalg.norm(embedding2)
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
        else:
            return dot_product / (magnitude1 * magnitude2)

    def _create_embedded_file(self, file_path: str):
        with open(file_path, "w"):
            pass
