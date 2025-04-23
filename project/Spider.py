import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import sqlite3
import uuid
import time
from Indexer import Indexer
import re
from ContentExtractor import ContentExtractor
from StopwordRemovalStem import StopwordRemovalStem # Import StopwordRemovalStem class


""" NOTES """
""" 
- look at the BFS (if it aligns with the max page limit)
- go through the code if everything matches with the requirements
- check if the database is being updated correctly and if there are any access conflicts 
"""



class Spider:
    def __init__(self, start_url: str, max_pages: int, db_connection: sqlite3.Connection, indexer: Indexer):
        self.start_url = start_url
        self.max_pages = max_pages

        self.visited_urls = set()
        self.url_queue = deque([start_url])
        self.enqueued_urls = set([start_url])

        # instead of connecting to database, we pass the connection to the spider to avoid database access conflicts
        self.db = db_connection  

        # enabling foreign key constraints allows updates to database without conflicts
        self.db.execute("PRAGMA foreign_keys = ON;")

        self.indexer = indexer
        self.extractor = ContentExtractor()
        self.stop_stem = StopwordRemovalStem()  # stopword removal and stemming part
        self.create_spider_tables()

    def create_spider_tables(self):
        with self.db:
            # 1. url_to_id
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS url_to_id (
                    url TEXT PRIMARY KEY,
                    urlId TEXT
                )
            ''')
            # 2. id_to_url
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS id_to_url (
                    urlId TEXT PRIMARY KEY,
                    url TEXT
                )
            ''')
            # 3. crawled_page_to_id
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS crawled_page_to_id (
                    url TEXT PRIMARY KEY,
                    urlId TEXT
                )
            ''')
            # 4. id_to_page_title
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS id_to_page_title (
                    urlId TEXT PRIMARY KEY,
                    pageTitle TEXT
                )
            ''')
            # 5. id_to_last_modification_date
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS id_to_last_modification_date (
                    urlId TEXT PRIMARY KEY,
                    lastModificationDate TEXT
                )
            ''')
            # 6. id_to_page_size
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS id_to_page_size (
                    urlId TEXT PRIMARY KEY,
                    pageSize TEXT
                )
            ''')
            # 7. id_to_children_url_id
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS id_to_children_url_id (
                    urlId TEXT PRIMARY KEY,
                    childrenUrlId TEXT
                )
            ''')
            # 8. id_to_parents_url_id
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS id_to_parents_url_id (
                    urlId TEXT PRIMARY KEY,
                    parentsUrlId TEXT
                )
            ''')

     # fetch the page from given url and return the response
    def fetch_page(self, url: str):
        try:
            # response = requests.get(url, timeout=10) # set timeout be 10 seconds
            response = requests.get(url) # set time out to be infinitely long
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            return None

    def get_or_create_url_id(self, url: str):
        """
        returns an existing urlId if found; otherwise creates a new uuid4
        and inserts into url_to_id, id_to_url, crawled_page_to_id
        """
        cursor = self.db.execute('SELECT urlId FROM url_to_id WHERE url = ?', (url,))
        row = cursor.fetchone()
        if row:
            return row[0]
        new_id = str(int(uuid.uuid4()))
        with self.db:
            self.db.execute('INSERT INTO url_to_id (url, urlId) VALUES (?, ?)', (url, new_id))
            self.db.execute('INSERT INTO id_to_url (urlId, url) VALUES (?, ?)', (new_id, url))
            self.db.execute('INSERT INTO crawled_page_to_id (url, urlId) VALUES (?, ?)', (url, new_id))
        return new_id

    def update_parents(self, child_id: str, parent_id: str):
        """
        append parent_id to child's parentsUrlId list, and child_id to parent's childrenUrlId list
        """
        # update child => parents
        cursor = self.db.execute('SELECT parentsUrlId FROM id_to_parents_url_id WHERE urlId = ?', (child_id,))
        row = cursor.fetchone()
        if row:
            current_parents = row[0] or ""
            if parent_id not in current_parents.split():
                updated_parents = (current_parents + " " + parent_id).strip()
                self.db.execute('UPDATE id_to_parents_url_id SET parentsUrlId=? WHERE urlId=?', (updated_parents, child_id))
        else:
            self.db.execute('INSERT INTO id_to_parents_url_id (urlId, parentsUrlId) VALUES (?, ?)', (child_id, parent_id))

        # update parent => children now
        cursor = self.db.execute('SELECT childrenUrlId FROM id_to_children_url_id WHERE urlId = ?', (parent_id,))
        row = cursor.fetchone()
        if row:
            current_children = row[0] or ""
            if child_id not in current_children.split():
                updated_children = (current_children + " " + child_id).strip()
                self.db.execute('UPDATE id_to_children_url_id SET childrenUrlId=? WHERE urlId=?', (updated_children, parent_id))
        else:
            self.db.execute('INSERT INTO id_to_children_url_id (urlId, childrenUrlId) VALUES (?, ?)', (parent_id, child_id))

     # major work is here
    def crawl(self):
        while self.url_queue and len(self.visited_urls) < self.max_pages:
            current_url = self.url_queue.popleft()
            if current_url in self.visited_urls:
                continue

            response = self.fetch_page(current_url)
            if not response:
                continue

            # build or fetch urlId. referencing previous function
            current_url_id = self.get_or_create_url_id(current_url)

            # the part where we utilize contentExtractor and Indexer to extract and index the content
            last_modified = self.extractor.getLastModDate(response.headers)
            page_title = self.extractor.getTitle(response.text)
            body_text = self.extractor.getBodyText(response.text)
            body_words = self.extractor.splitWords(body_text)
            processed_body_words = self.stop_stem.transform(body_words)  # lastly added stopstem part
            self.indexer.addNewWord(processed_body_words)
            self.indexer.buildBodyInvertedIndex(processed_body_words, current_url_id)
            self.indexer.buildForwardIndex(processed_body_words, current_url_id)

            # here we go one step further and index the title as well
            if page_title:
                title_words = self.extractor.splitWords(page_title.lower())
                processed_title_words = self.stop_stem.transform(title_words)  # do stopstem for this too
                self.indexer.addNewWord(processed_title_words)
                self.indexer.buildTitleInvertedIndex(processed_title_words, current_url_id)
                self.indexer.buildForwardIndex(processed_title_words, current_url_id)

            # update DB after indexing is finished
            self.indexer.updateSQLiteDB()

            page_size = str(self.extractor.getPagesize(response.headers, body_text))

            # update last modification date, page title, page size
            with self.db:
                self.db.execute('INSERT OR REPLACE INTO id_to_last_modification_date (urlId, lastModificationDate) VALUES (?, ?)',
                                (current_url_id, last_modified))
                # Update page title
                self.db.execute('INSERT OR REPLACE INTO id_to_page_title (urlId, pageTitle) VALUES (?, ?)',
                                (current_url_id, page_title))
                # Update page size
                self.db.execute('INSERT OR REPLACE INTO id_to_page_size (urlId, pageSize) VALUES (?, ?)',
                                (current_url_id, page_size))

            self.visited_urls.add(current_url)

            # extract links from the hyperlink
            links = self.extractor.getLinks(current_url, response.text)
            for link in links:
                # below line prevents cyclic links by avoiding already visited and enqueued urls
                if link not in self.visited_urls and link not in self.enqueued_urls:
                    self.url_queue.append(link)
                    self.enqueued_urls.add(link)
                child_id = self.get_or_create_url_id(link)
                # after extracting a new id, update child's parent and parent's child
                self.update_parents(child_id, current_url_id)

            print(f"Crawled: {current_url} ({current_url_id})")

       
        # bonus: summary info on database
        cursor = self.db.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print("Database Summary:")
        for table in tables:
            # counts for general info
            count = self.db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"Table '{table}' has {count} rows.")

            # also added columns info
            column_info = self.db.execute(f"PRAGMA table_info({table})").fetchall()
            print("Columns:")
            for col in column_info:
                print(f"  {col[1]} ({col[2]})")
            print()


if __name__ == "__main__":
    # thread-safe connection
    db_connection = sqlite3.connect("main.db", check_same_thread=False)  
    db_connection.execute("PRAGMA journal_mode=WAL;")  # for concurrency issues, allow WAL mode
    indexer = Indexer(db_connection)  # pass shared connection to Indexer
    spider = Spider(
        start_url="https://www.cse.ust.hk/~kwtleung/COMP4321/testpage.htm",
        max_pages=300,
        db_connection=db_connection,  # pass shared connection to Spider
        indexer=indexer
    )
    spider.crawl()
    db_connection.close()  # close the connection after crawling


