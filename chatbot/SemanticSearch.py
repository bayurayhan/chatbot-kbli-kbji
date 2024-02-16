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
        self.db_path = get_path("chatbot", "data", "baku.db")
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
            {"temperature": 0.9, "top_k": 1, "top_p": 1, "max_output_tokens": 5000},
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
                    f"{i + 1}. kode_{data_name}: {doc.metadata['kode']}; nama: {doc.metadata['source']}"
                )
        else:
            for i, doc in enumerate(results):
                row_data = read_specific_row(
                    get_path("chatbot", "data", f"{data_name}_embedding.csv"),
                    doc.metadata.get("row"),
                )
                results_string.append(
                    f"{i + 1}. kode_{data_name}: {doc.metadata.get('source')}; nama: {row_data['judul']}; deskripsi: {row_data['deskripsi']}"
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

            # df["judul_deskripsi"] = df["judul"] + "\n" + df["deskripsi"]
            # df["judul_deskripsi_embedding"] = await self.embedding_model.get_embedding(
            #     df["judul_deskripsi"].to_list()
            # )

            # del df["judul_deskripsi"]
            # df_new = pd.DataFrame()
            # df_new["nama lapangan usaha"] = df["judul"]
            # df_new["deskripsi"] = df["deskripsi"]

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

    def _load_embedding_data(
        self, data_name=None, intent: Intent = Intent.MENCARI_KODE
    ) -> FAISS:
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
                get_path("chatbot", "data", f"{data_name}_embedding.csv"),
                source_column="judul",
                metadata_columns=["kode", "deskripsi"],
            )
            documents = loader.load()

            # # Load to FAISS database
            db_mencari_kode = FAISS.from_documents(
                documents, self.embedding_model.get_model()
            )
            db_mencari_kode.save_local(
                get_path(faiss_folder, Intent.MENCARI_KODE.value)
            )
            # ==========================================================================
            logger.info("Load the kode documents...")

            loader = CSVLoader(
                get_path("chatbot", "data", f"{data_name}_kode_embedding.csv"),
                source_column="kode",
            )
            documents = loader.load()

            db_menjelaskan_kode = FAISS.from_documents(
                documents, self.embedding_model.get_model()
            )
            db_menjelaskan_kode.save_local(
                get_path(faiss_folder, Intent.MENJELASKAN_KODE.value)
            )

            return (
                db_mencari_kode
                if intent == Intent.MENCARI_KODE
                else Intent.MENJELASKAN_KODE
            )

        # db = FAISS.load_local(faiss_folder, self.embedding_model.get_model())
        folder_name = os.path.join(faiss_folder, intent.value)
        db = FAISS.load_local(folder_name, self.embedding_model.get_model())
        return db

    def _create_embedded_file(self, file_path: str):
        with open(file_path, "w"):
            pass
