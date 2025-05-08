# FILE: Retrieval.py
import sqlite3
import math
import re
from collections import defaultdict
from StopwordRemovalStem import StopwordRemovalStem


class Retrieval:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.stop_stem = StopwordRemovalStem()

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
        # skip terms where doc_count is 0 to avoid division by zero (according to TA answer)
        if doc_count == 0:
            return 0
        
        tf = term_frequency / max_tf
        idf = math.log2(total_docs / doc_count)  # Removed the +1
        return tf * idf

    def cosine_similarity(self, query_vector, doc_vector):
        dot_product = sum(query_vector[term] * doc_vector.get(term, 0) for term in query_vector)
        query_magnitude = math.sqrt(sum(weight ** 2 for weight in query_vector.values()))
        doc_magnitude = math.sqrt(sum(weight ** 2 for weight in doc_vector.values()))
        if query_magnitude == 0 or doc_magnitude == 0:
            return 0
        return dot_product / (query_magnitude * doc_magnitude)

    def parse_query_with_phrases(self, query):
        import re
        pattern = r'"([^"]+)"|\b\w+\b'
        tokens = []
        for match in re.finditer(pattern, query.strip().lower()):
            if match.group(1):
                tokens.append(match.group(1))
            else:
                tokens.append(match.group(0))
        return tokens

    def phrase_in_postings(self, phrase_word_ids, inverted_index):
        """
        Returns a set of doc_ids where the phrase (list of word_ids) appears consecutively.
        """
        if not phrase_word_ids:
            return set()
        #get postings for each word in the phrase
        postings_lists = []
        for wid in phrase_word_ids:
            postings = inverted_index.get(wid, {})
            postings_lists.append(postings)
        # find common doc_ids
        common_doc_ids = set(postings_lists[0].keys())
        for postings in postings_lists[1:]:
            common_doc_ids &= set(postings.keys())
        result_docs = set()
        for doc_id in common_doc_ids:
            # get positions for each word in this doc
            positions_lists = [postings[doc_id]["positions"] for postings in postings_lists]
            # for the first word, check if there is a sequence of positions for the phrase
            first_positions = positions_lists[0]
            for pos in first_positions:
                match = True
                for offset in range(1, len(positions_lists)):
                    if (pos + offset) not in positions_lists[offset]:
                        match = False
                        break
                if match:
                    result_docs.add(doc_id)
                    break
        return result_docs

    def retrieve(self, query, max_results=50):
        if not query.strip():
            print("The query is empty. Please provide a valid query.")
            return []
        print(f"Raw query: '{query}'")

        body_inverted_index = self.load_inverted_index()
        title_inverted_index = self.load_title_index()

        query_terms = self.parse_query_with_phrases(query)
        print(f"Query terms (with phrases): {query_terms}")

        # stem and remove stopwords from query terms
        processed_query_terms = []
        for term in query_terms:
            if " " in term:  # phrase
                words = term.split()
                processed_words = self.stop_stem.transform(words)
                if processed_words:
                    processed_query_terms.append(" ".join(processed_words))
            else:
                processed = self.stop_stem.transform([term])
                if processed:
                    processed_query_terms.append(processed[0])
        print(f"Processed query terms (with phrases): {processed_query_terms}")

        # map query terms to word IDs based on database schema
        query_word_ids = []
        phrase_word_ids_list = []
        single_terms_set = set()
        for term in processed_query_terms:
            if " " in term:  # phrase
                words = term.split()
                word_ids = []
                for w in words:
                    self.cursor.execute("SELECT wordId FROM word_to_id WHERE word = ?", (w,))
                    row = self.cursor.fetchone()
                    if row:
                        word_ids.append(row[0])
                        # ad each word in phrase as a single term if not already present
                        if w not in single_terms_set:
                            single_terms_set.add(w)
                if word_ids:
                    phrase_word_ids_list.append(word_ids)
            else:
                single_terms_set.add(term)

        #process all single terms (including those from phrases)
        for term in single_terms_set:
            self.cursor.execute("SELECT wordId FROM word_to_id WHERE word = ?", (term,))
            row = self.cursor.fetchone()
            print(f"Term: {term}, Word ID: {row}")
            if row:
                query_word_ids.append(row[0])  # add the wordId to the list if term exists in the database

        # build query vector for single terms
        query_vector = defaultdict(float)
        for word_id in query_word_ids:
            if word_id in body_inverted_index:
                query_vector[word_id] += 1

        # phrase search: get doc_ids that match all phrases in body or title
        phrase_doc_sets = []
        for phrase_word_ids in phrase_word_ids_list:
            body_docs = self.phrase_in_postings(phrase_word_ids, body_inverted_index)
            title_docs = self.phrase_in_postings(phrase_word_ids, title_inverted_index)
            phrase_doc_sets.append(body_docs | title_docs)
        # If there are phrase queries, only keep docs that match all phrases
        if phrase_doc_sets:
            docs_with_phrases = set.intersection(*phrase_doc_sets) if phrase_doc_sets else set()
        else:
            docs_with_phrases = None  # no phrase constraint

        # check if query_vector is empty and no phrase matches
        if not query_vector and not phrase_doc_sets:
            print("No matching terms found in the index for the given query.")
            return []

        # normalize query vector based on max tf
        if query_vector:
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
            if word_id in title_inverted_index:
                title_postings = title_inverted_index[word_id]
                # boost score if word is in title
                for doc_id in title_postings:
                    doc_scores[doc_id] += 7 

        # for phrase matches, boost their score, with extra boost if phrase is in title
        if phrase_doc_sets:
            for idx, phrase_word_ids in enumerate(phrase_word_ids_list):
                body_docs = self.phrase_in_postings(phrase_word_ids, body_inverted_index)
                title_docs = self.phrase_in_postings(phrase_word_ids, title_inverted_index)
                for doc_id in docs_with_phrases:
                    if doc_id in title_docs:
                        doc_scores[doc_id] += 10  # higher boost for phrase in title
                    elif doc_id in body_docs:
                        doc_scores[doc_id] += 3  # normal boost for phrase in body

        # finally rank documents by score
        ranked_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)[:max_results]

        # fetch metadata of ranked documents to display
        results = []
        for doc_id, score in ranked_docs:

            # get the page title
            self.cursor.execute("SELECT pageTitle FROM id_to_page_title WHERE urlId = ?", (doc_id,))
            title_row = self.cursor.fetchone()
            title = title_row[0] if title_row else None

            # get the page URL
            self.cursor.execute("SELECT url FROM id_to_url WHERE urlId = ?", (doc_id,))
            url_row = self.cursor.fetchone()
            url = url_row[0] if url_row else None

            # get the last modification date
            self.cursor.execute("SELECT lastModificationDate FROM id_to_last_modification_date WHERE urlId = ?", (doc_id,))
            last_modification_date_row = self.cursor.fetchone()
            last_modification_date = last_modification_date_row[0] if last_modification_date_row else None

            # get the size of the page
            self.cursor.execute("SELECT pageSize FROM id_to_page_size WHERE urlId = ?", (doc_id,))
            page_size_row = self.cursor.fetchone()
            page_size = page_size_row[0] if page_size_row else None

            # if URL or title or other critical info is missing, skip this result
            if not url:
                continue

            # get the keyword frequency pairs (get the top 5 most frequent stemmed keywords)
            frequency_dict = {}
            # iterate over all word IDs in the body_inverted_index
            for word_id, postings in body_inverted_index.items():
                if doc_id in postings:
                    freq = postings[doc_id]["frequency"]
                    self.cursor.execute("SELECT word FROM id_to_word WHERE wordId = ?", (word_id,))
                    word_row = self.cursor.fetchone()
                    word = word_row[0] if word_row else "N/A"
                    # only consider words - alphabetic (filter out numbers)
                    if word and word != "N/A" and word.isalpha():
                        frequency_dict[word] = freq

            # sort the dictionary by frequency and get the top 5
            top_keywords = sorted(frequency_dict.items(), key=lambda item: item[1], reverse=True)[:5]

            # format the output as needed
            keywords_frequencies = [f"{word} {freq}" for word, freq in top_keywords]
            top5FrequentKeywords = " ".join([word for word, _ in top_keywords if word])

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
                            "title": title if title else "(No Title)",
                            "url": url,
                            "last_modification_date": last_modification_date if last_modification_date else "(No Date)",
                            "page_size": page_size if page_size else "(No Size)",
                            "keywords_frequencies": keywords_frequencies,
                            "parent_links": parent_links,
                            "child_links": child_links,
                            "top5FrequentKeywords": top5FrequentKeywords,
                            })

        return results
    
    # For BONUS: allows user to query the stemmed words from database
    def get_all_keywords(self):
        self.cursor.execute("SELECT word FROM word_to_id;")
        rows = self.cursor.fetchall()

        all_keywords = [row[0] for row in rows]

        return all_keywords

if __name__ == "__main__":
    retrieval = Retrieval("main.db")
    query = 'classification for "information retrieval"'
    results = retrieval.retrieve(query)

    for result in results:
        print(f'Document ID: {result["doc_id"]}')
        print(f'Score: {result["score"]}')
        print(f'Title: {result["title"]}')
        print(f'URL: {result["url"]}')
        print(f'Last Modification Date: {result["last_modification_date"]}')
        print(f'Page Size: {result["page_size"]}')
        print(f'Keywords and Frequencies: {"; ".join(result["keywords_frequencies"])}')
        print(f'Parent Links:')
        for link in result["parent_links"]:
            print(link)
        print(f'Child Links:')
        for link in result["child_links"]:
            print(link)
        print(f'Top 5 Frequent Keywords: {result["top5FrequentKeywords"]}')
        print("\n")