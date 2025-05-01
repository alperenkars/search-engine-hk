# FILE: Retrieval.py
import sqlite3
import math
import re
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

            # get the page title
            self.cursor.execute("SELECT pageTitle FROM id_to_page_title WHERE urlId = ?", (doc_id,))
            title_row = self.cursor.fetchone()
            title = title_row[0] if title_row else "N/A"

            # get the page URL
            self.cursor.execute("SELECT url FROM id_to_url WHERE urlId = ?", (doc_id,))
            url_row = self.cursor.fetchone()
            url = url_row[0] if url_row else "N/A"

            # get the last modification date
            self.cursor.execute("SELECT lastModificationDate FROM id_to_last_modification_date WHERE urlId = ?", (doc_id,))
            last_modification_date_row = self.cursor.fetchone()
            last_modification_date = last_modification_date_row[0] if last_modification_date_row else "N/A"

            # get the size of the page
            self.cursor.execute("SELECT pageSize FROM id_to_page_size WHERE urlId = ?", (doc_id,))
            page_size_row = self.cursor.fetchone()
            page_size = page_size_row[0] if page_size_row else "N/A"

            # get the keyword frequency pairs (get the top 5 most frequent stemmed keywords)
            self.cursor.execute("SELECT value FROM forward_index WHERE urlId = ?", (doc_id,))
            word_ids_row = self.cursor.fetchone()
            word_ids = word_ids_row[0].split()[:10] if word_ids_row else []

            frequency_dict = {}

            for word_id in word_ids:
                self.cursor.execute("SELECT word FROM id_to_word WHERE wordId = ?", (word_id,))
                word_row = self.cursor.fetchone()
                word = word_row[0] if word_row else "N/A"

                self.cursor.execute("SELECT value FROM body_inverted_index WHERE wordId = ?", (word_id,))
                body_data_row = self.cursor.fetchone()
                body_data = body_data_row[0] if body_data_row else ""

                for entry in body_data.split():
                    entry_url_id, freq, _ = entry.split(";")
                    if entry_url_id == doc_id:
                        # Update the frequency in the dictionary
                        frequency_dict[word] = frequency_dict.get(word, 0) + int(freq)
                        break

            # Sort the dictionary by frequency and get the top 5
            top_keywords = sorted(frequency_dict.items(), key=lambda item: item[1], reverse=True)[:5]

            # Format the output as needed
            keywords_frequencies = [f"{word} {freq}" for word, freq in top_keywords]


            # get the parent links
            self.cursor.execute("SELECT parentsUrlId FROM id_to_parents_url_id WHERE urlId = ?", (doc_id,))
            parents_row = self.cursor.fetchone()
            parent_links = []
            if parents_row:
                parent_ids = parents_row[0].split()[:10]
                for parent_id in parent_ids:
                    self.cursor.execute("SELECT url FROM id_to_url WHERE urlId = ?", (parent_id,))
                    parent_url_row = self.cursor.fetchone()
                    parent_links.append(parent_url_row[0] if parent_url_row else "This page has no parent link.")

            # get the child links
            self.cursor.execute("SELECT childrenUrlId FROM id_to_children_url_id WHERE urlId = ?", (doc_id,))
            children_row = self.cursor.fetchone()
            child_links = []
            if children_row:
                child_ids = children_row[0].split()[:10]
                for child_id in child_ids:
                    self.cursor.execute("SELECT url FROM id_to_url WHERE urlId = ?", (child_id,))
                    child_url_row = self.cursor.fetchone()
                    child_links.append(child_url_row[0] if child_url_row else "This page has no child link.")
            

            results.append({"doc_id": doc_id,
                            "score": score,
                            "title": title,
                            "url": url,
                            "last_modification_date": last_modification_date,
                            "page_size": page_size,
                            "keywords_frequencies": keywords_frequencies,
                            "parent_links": parent_links,
                            "child_links": child_links
                            })

            # results.append({"doc_id": doc_id, "url": url, "title": title, "score": score})

        return results

if __name__ == "__main__":
    retrieval = Retrieval("main.db")
    query = 'gordon brown'
    results = retrieval.retrieve(query)

    for result in results:
        """
        print(f
        Doc ID: {result['doc_id']}, 
        Score: {result['score']},
        Title: {result['title']},
        URL: {result['url']},
        Last Modification Date: {result['last_modification_date']},
        Page Size: {result['page_size']},
        Keywords and Frequencies: 
        {"; ".join(result['keywords_frequencies'])}

        Parent links: 
        {"\n".join(result['parent_links'])}

        Child links: 
        {"\n".join(result['child_links'])}
        )
        """
        # print(f"\nDoc ID: {result['doc_id']}, \nURL: {result['url']}, \nTitle: {result['title']}, \nScore: {result['score']}")
    