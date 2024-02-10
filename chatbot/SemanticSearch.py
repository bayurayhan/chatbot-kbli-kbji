# TODO: Implement semantic search using Embedding
# 1. Find the right library to help me doing this
# 2. Create abstraction for sure
# 3. Find way how to handle the data. Our data is a sqlite database
import sqlite3
import openai

class SemanticSearch:
    def __init__(self, api_key, db_path):
        openai.api_key = api_key
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def get_embedding(self, text):
        response = openai.Embedding.create(model="text-davinci-003", input=text)
        return response['embedding']

    def semantic_search(self, query_text, top_n=5):
        query_embedding = self.get_embedding(query_text)
        self.cursor.execute('''
            SELECT kode, judul, deskripsi
            FROM kbli_2020
        ''')
        kbli_2020_results = self.cursor.fetchall()

        self.cursor.execute('''
            SELECT kode, judul, deskripsi
            FROM kbji_2014
        ''')
        kbji_2014_results = self.cursor.fetchall()

        all_results = kbli_2020_results + kbji_2014_results
        scored_results = []

        for result in all_results:
            kode, judul, deskripsi = result
            embedding = self.get_embedding(deskripsi)
            similarity_score = self.calculate_similarity(query_embedding, embedding)
            scored_results.append((kode, judul, similarity_score))

        scored_results.sort(key=lambda x: x[2], reverse=True)
        return scored_results[:top_n]

    def calculate_similarity(self, embedding1, embedding2):
        # Implement your similarity calculation method here
        # This can be cosine similarity, Euclidean distance, etc.
        pass

    def close_connection(self):
        self.conn.close()