# FILE: Retrieval.py
import sqlite3
import math
from collections import defaultdict

# look for NA issues and try with more than 300 pages!


class Retrieval:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def load_inverted_index(self):
        self.cursor.execute("SELECT * FROM body_inverted_index;")
        body_inverted_index = {}
        for word_id, value in self.cursor.fetchall():
            postings = {}
            for entry in value.split():
                url_id, frequency, *positions = entry.split(";")
                postings[url_id] = {
                    "frequency": int(frequency),
                    "positions": list(map(int, positions[0].split(",")))  # split positions by commas (?)
                }
            body_inverted_index[word_id] = postings
        return body_inverted_index

    def load_title_index(self):
        self.cursor.execute("SELECT * FROM title_inverted_index;")
        title_inverted_index = {}
        for word_id, value in self.cursor.fetchall():
            postings = {}
            for entry in value.split():
                url_id, frequency, *positions = entry.split(";")
                postings[url_id] = {
                    "frequency": int(frequency),
                    "positions": list(map(int, positions[0].split(","))) 
                }
            title_inverted_index[word_id] = postings
        return title_inverted_index

    def calculate_tfxidf(self, term_frequency, max_tf, doc_count, total_docs):
        tf = term_frequency / max_tf
        idf = math.log(total_docs / (1 + doc_count))
        return tf * idf

    def cosine_similarity(self, query_vector, doc_vector):
        dot_product = sum(query_vector[term] * doc_vector.get(term, 0) for term in query_vector)
        query_magnitude = math.sqrt(sum(weight ** 2 for weight in query_vector.values()))
        doc_magnitude = math.sqrt(sum(weight ** 2 for weight in doc_vector.values()))
        if query_magnitude == 0 or doc_magnitude == 0:
            return 0
        return dot_product / (query_magnitude * doc_magnitude)

    def retrieve(self, query, max_results=50):

        # check if the query is empty
        if not query.strip():
            print("The query is empty. Please provide a valid query.")
            return []
        print(f"Raw query: '{query}'")
       

        # load inverted indexes
        body_inverted_index = self.load_inverted_index()
        title_inverted_index = self.load_title_index()
        # tokenize query and handle phrases (phrase search)
        import re
        query_terms = re.findall(r'\b\w+\b', query.lower())

        # test if query terms are passed correctly
        print(f"Query terms: {query_terms}")

        # map query terms to word IDs based on database schema
        query_word_ids = []
        for term in query_terms:
            self.cursor.execute("SELECT wordId FROM word_to_id WHERE word = ?", (term,))
            row = self.cursor.fetchone()

            # test
            print(f"Term: {term}, Word ID: {row}")

            if row:
                query_word_ids.append(row[0])  # add the wordId to the list if term exists in the database

        

        # build query vector
        query_vector = defaultdict(float)
        for word_id in query_word_ids:
            if word_id in body_inverted_index:
                query_vector[word_id] += 1

        # check if query_vector is empty
        if not query_vector:
            print("No matching terms found in the index for the given query.")
            return []

        # normalize query vector based on max tf
        max_tf_query = max(query_vector.values())
        for word_id in query_vector:
            query_vector[word_id] /= max_tf_query

        # calculate document scores
        doc_scores = defaultdict(float)
        total_docs = len(body_inverted_index)

        for word_id, query_weight in query_vector.items():
            if word_id in body_inverted_index:
                postings = body_inverted_index[word_id]
                doc_count = len(postings)
                for doc_id, data in postings.items():
                    tfidf = self.calculate_tfxidf(data["frequency"], max(data["frequency"] for data in postings.values()), doc_count, total_docs)
                    doc_scores[doc_id] += query_weight * tfidf

            # boost title matches (as specified in the handout)
            if word_id in title_inverted_index:
                title_postings = title_inverted_index[word_id]
                for doc_id in title_postings:
                    # our structure involves boosting score by 1 for each word match in title
                    doc_scores[doc_id] += 1  

        # finally rank documents by score
        ranked_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)[:max_results]

        # fetch metadata of ranked documents to display
        results = []
        for doc_id, score in ranked_docs:
            self.cursor.execute("SELECT url FROM id_to_url WHERE urlId = ?", (doc_id,))
            url_row = self.cursor.fetchone()
            url = url_row[0] if url_row else "N/A"

            self.cursor.execute("SELECT pageTitle FROM id_to_page_title WHERE urlId = ?", (doc_id,))
            title_row = self.cursor.fetchone()
            title = title_row[0] if title_row else "N/A"

            results.append({"doc_id": doc_id, "url": url, "title": title, "score": score})

        return results

if __name__ == "__main__":
    retrieval = Retrieval("main.db")
    query = 'death star'
    results = retrieval.retrieve(query)
    for result in results:
        print(f"\nDoc ID: {result['doc_id']}, \nURL: {result['url']}, \nTitle: {result['title']}, \nScore: {result['score']}")