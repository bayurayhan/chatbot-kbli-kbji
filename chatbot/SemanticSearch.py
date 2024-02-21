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
from langchain.text_splitter import (
    TokenTextSplitter,
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from .templates import prompt_templates
from .IntentClassifier import Intent

logger = logging.getLogger("app")


class SemanticSearch:
    def __init__(
        self, embedding_model: EmbeddingModel, text_generator: GenerativeModel
    ):
        """Initialize the class

        Args:
            embedding_model (EmbeddingModel): _description_
        """
        self.embedding_model = embedding_model
        self.text_generator = text_generator

        embedded_file_path = get_path("chatbot", "data", ".EMBEDDED")
        if not os.path.exists(embedded_file_path):
            logger.info(
                "Creating embedding for the database. This may take some time..."
            )
            self._embed_database()
            self._create_embedded_file(embedded_file_path)

        self._load_embedding_data("kbli2020")
        self._load_embedding_data("kbji2014")

    async def _preprocessing_query(self, query: str) -> str:
        templated = prompt_templates.preprocessing_query(query)
        processed_query = await self.text_generator.generate_text(
            templated,
            {"temperature": 0, "top_p": 1, "max_output_tokens": 5000},
        )
        logger.debug(f"Preprocessing query: {processed_query}")
        return processed_query

    async def embedding_query_to_text(
        self,
        query: str,
        digit: int = None,
        data_name="kbli2020",
        intent: Intent = Intent.MENCARI_KODE,
    ):
        """
        Embed query into text string

        Args:
            query (str): _description_

        Returns:
            list (str): List of outputs ready to print.
        """
        if intent == Intent.MENCARI_KODE:
            processed_query = await self._preprocessing_query(query)
            if digit:
                processed_query = f"{digit} digit\n" + processed_query
        else:
            processed_query = f"kode_{data_name}: " + query

        db = self._load_embedding_data(data_name, intent=intent)

        # NOTE: You can use different types of retrieval algorithms, such as similarity search, max marginal relevance search, self query, contextual compression, time-weighted search, and multi-query retriever.
        k = 10 if intent == Intent.MENCARI_KODE else 3
        results = db.similarity_search(query=processed_query, k=k)

        results_string = []

        if intent == Intent.MENCARI_KODE:
            for i, doc in enumerate(results):
                results_string.append(
                    f"{i + 1}. kode_{data_name}: {doc.metadata['kode']}; nama: {doc.metadata['source']};"
                )
        else:
            for i, doc in enumerate(results):
                row_data = read_specific_row(
                    get_path("chatbot", "data", f"{data_name}_embedding.csv"),
                    doc.metadata.get("row"),
                )
                results_string.append(
                    f"{i + 1}. kode_{data_name}: {doc.metadata.get('source')}; nama: {row_data['judul']}; deskripsi: {row_data['deskripsi']};"
                )
        return results_string, processed_query

    def _embed_database(self):
        logger.info("Embedding the database")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._process_embedding("kbli2020"))
        loop.run_until_complete(self._process_embedding("kbji2014"))
        logger.info("Finished embedding the database!")

    async def _process_embedding(self, data_name: str):
        try:
            embedded_file_path = get_path(
                "chatbot", "data", f"{data_name}_embedding.csv"
            )
            if os.path.exists(embedded_file_path):
                logger.info(f"Skipping {data_name} embedding.")
                return

            column_types = {"kode": "str"}

            df = pd.read_csv(
                get_path("chatbot", "data", f"{data_name}.csv"),
                dtype=column_types,
            )

            df["deskripsi"] = df["deskripsi"].fillna("unknown")

            df.to_csv(
                get_path("chatbot", "data", f"{data_name}_embedding.csv"),
                index=False,
            )
            df["kode"].to_csv(
                get_path("chatbot", "data", f"{data_name}_kode_embedding.csv"),
                index=False,
            )
            logger.info(f"Successfully generating embbeding for {data_name}")

        except Exception as e:
            logger.error(e)
            raise RuntimeError(
                "Error when embedding the database, please check the log file."
            )

    def _load_documents(self, data_name: str, intent: Intent) -> list[str]:
        """
        Load documents from CSV file and split them into chunks.

        Args:
            data_name (str): Name of the data
            intent (Intent): Intent enum value

        Returns:
            List[str]: List of documents
        """
        source_column = "judul" if intent == Intent.MENCARI_KODE else ("kode" if intent == Intent.MENJELASKAN_KODE else None)
        metadata_columns = ["kode", "deskripsi"] if intent == Intent.MENCARI_KODE else None
        
        loader = CSVLoader(
            get_path("chatbot", "data", f"{data_name}_embedding.csv"),
            source_column=source_column,
            metadata_columns=metadata_columns
        )
        documents = loader.load()
        if not intent == Intent.MENJELASKAN_KODE:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=10)
            documents = text_splitter.split_documents(documents)
        return documents

    def _embed_documents(self, documents: list[str], save_folder: str) -> FAISS:
        """
        Embed documents and save the embeddings to the specified folder.

        Args:
            documents (List[str]): List of documents to embed
            save_folder (str): Folder path to save embeddings

        Returns:
            FAISS: Embedded documents
        """
        db = self.embedding_model.faiss_embedding(documents=documents, save_folder=save_folder)
        return db

    def _load_embedding_data(
        self, data_name: str = None, intent: Intent = Intent.MENCARI_KODE
    ) -> FAISS:
        """
        Load embedded data from CSV files or embed them if necessary.

        Args:
            data_name (str, optional): Name of the data. Defaults to None.
            intent (Intent, optional): Intent enum value. Defaults to Intent.MENCARI_KODE.

        Returns:
            FAISS: Embedded data
        """
        faiss_folder = os.path.join("chatbot", "data", f"{data_name}_faiss_index")

        if not os.path.exists(faiss_folder):
            logger.info("Load the documents...")
            documents = self._load_documents(data_name, intent)

            if intent == Intent.MENCARI_KODE:
                save_folder = get_path(faiss_folder, Intent.MENCARI_KODE.value)
            else:
                save_folder = get_path(faiss_folder, Intent.MENJELASKAN_KODE.value)

            db = self._embed_documents(documents, save_folder)
        else:
            folder_name = os.path.join(faiss_folder, intent.value)
            db = self.embedding_model.load_faiss_embedding(folder_name)

        return db


    def _create_embedded_file(self, file_path: str):
        with open(file_path, "w"):
            pass
