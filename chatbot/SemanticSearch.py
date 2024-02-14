import logging
from .utils import get_path, read_specific_row
import os
from .Model import EmbeddingModel, GenerativeModel
from .TextGeneration import TextGeneration
import numpy as np
import pandas as pd
from tqdm.auto import tqdm
import asyncio
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores.faiss import FAISS
from langchain.text_splitter import TokenTextSplitter, CharacterTextSplitter
from .templates import prompt_templates

logger = logging.getLogger("app")


class SemanticSearch:
    def __init__(self, embedding_model: EmbeddingModel, text_generator: TextGeneration):
        """Initialize the class

        Args:
            embedding_model (EmbeddingModel): _description_
        """
        self.db_path = get_path(os.path.join("chatbot", "data", "baku.db"))
        self.embedding_model = embedding_model
        self.text_generator = text_generator

        embedded_file_path = get_path(os.path.join("chatbot", "data", ".EMBEDDED"))
        if not os.path.exists(embedded_file_path):
            logger.info(
                "Creating embedding for the database. This may take some time..."
            )
            self._embed_database()
            self._create_embedded_file(embedded_file_path)

        db = self._load_embedding_data("kbli2020")
    
    async def _preprocessing_query(self, query: str) -> str:
        templated = prompt_templates.preprocessing_query(query)
        processed_query = await self.text_generator.generate(templated)
        logger.debug(processed_query)
        return processed_query

    async def embedding_query_to_text(self, query: str, digit: int = None):
        """
        Embed query into text string

        Args:
            query (str): _description_

        Returns:
            list (str): List of outputs ready to print.
        """
        processed_query = await self._preprocessing_query(query)
        if digit:
            processed_query = f"{digit} digit\n" + processed_query
        
        db = self._load_embedding_data("kbli2020")
        # NOTE: You can use different types of retrieval algorithms, such as similarity search, max marginal relevance search, self query, contextual compression, time-weighted search, and multi-query retriever.
        results = db.similarity_search_with_score(processed_query, k=5)

        results_string = []

        for i, (doc, score) in enumerate(results):
            results_string.append(f"{i + 1}. [{doc.metadata['kode']}] {doc.metadata['source']}")

        return results_string

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

            # df["judul_deskripsi"] = df["judul"] + "\n" + df["deskripsi"]
            # df["judul_deskripsi_embedding"] = await self.embedding_model.get_embedding(
            #     df["judul_deskripsi"].to_list()
            # )

            # del df["judul_deskripsi"]
            # df_new = pd.DataFrame()
            # df_new["nama lapangan usaha"] = df["judul"]
            # df_new["deskripsi"] = df["deskripsi"]

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
                source_column="judul",
                metadata_columns=["kode"]
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

    def _create_embedded_file(self, file_path: str):
        with open(file_path, "w"):
            pass
