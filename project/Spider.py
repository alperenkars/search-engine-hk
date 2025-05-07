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
from StopwordRemovalStem import StopwordRemovalStem  # Import StopwordRemovalStem class

import asyncio
import aiohttp
from asyncio import Queue


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

    def clear_spider_tables(self):
         # to see the results clearly
        with self.db:
            self.db.execute("DELETE FROM url_to_id")
            self.db.execute("DELETE FROM id_to_url")
            self.db.execute("DELETE FROM crawled_page_to_id")
            self.db.execute("DELETE FROM id_to_page_title")
            self.db.execute("DELETE FROM id_to_last_modification_date")
            self.db.execute("DELETE FROM id_to_page_size")
            self.db.execute("DELETE FROM id_to_children_url_id")
            self.db.execute("DELETE FROM id_to_parents_url_id")
        # also clear indexer tables 
        self.indexer.prepareSQLiteDB()
        self.indexer.updateSQLiteDB()

    async def fetch_page(self, session, url: str):
        try:
            async with session.get(url) as response:
                try:
                    # try normally decode first 
                    text = await response.text()
                except UnicodeDecodeError:
                    # if error, read the raw bytes and try latin1 decoding
                    raw = await response.read()
                    try:
                        text = raw.decode('latin1')
                    except Exception:
                        text = raw.decode('utf-8', errors='replace')
                headers = dict(response.headers)
                return type('Response', (), {'text': text, 'headers': headers, 'url': url})
        except Exception as e:
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

    async def worker(self, session, url_queue: Queue, batch, batch_size, stop_event):
        while not stop_event.is_set():
            try:
                current_url, parent_url_id = await asyncio.wait_for(url_queue.get(), timeout=1)
            except asyncio.TimeoutError:
                if stop_event.is_set():
                    break
                continue
            if current_url in self.visited_urls:
                url_queue.task_done()
                continue

            response = await self.fetch_page(session, current_url)
            if not response:
                url_queue.task_done()
                continue

            current_url_id = self.get_or_create_url_id(current_url)

            last_modified = self.extractor.getLastModDate(response.headers)
            page_title = self.extractor.getTitle(response.text)
            body_text = self.extractor.getBodyText(response.text)
            body_words = self.extractor.splitWords(body_text)
            processed_body_words = self.stop_stem.transform(body_words)
            self.indexer.addNewWord(processed_body_words)
            self.indexer.buildBodyInvertedIndex(processed_body_words, current_url_id)
            self.indexer.buildForwardIndex(processed_body_words, current_url_id)

            if page_title:
                title_words = self.extractor.splitWords(page_title.lower())
                processed_title_words = self.stop_stem.transform(title_words)
                self.indexer.addNewWord(processed_title_words)
                self.indexer.buildTitleInvertedIndex(processed_title_words, current_url_id)
                self.indexer.buildForwardIndex(processed_title_words, current_url_id)

            page_size = str(self.extractor.getPagesize(response.headers, body_text))

            batch.append((
                current_url_id, last_modified, page_title, page_size
            ))

            self.visited_urls.add(current_url)

            links = self.extractor.getLinks(current_url, response.text)
            for link in links:
                if link not in self.visited_urls and link not in self.enqueued_urls:
                    url_queue.put_nowait((link, current_url_id))
                    self.enqueued_urls.add(link)
                child_id = self.get_or_create_url_id(link)
                self.update_parents(child_id, current_url_id)

            url_queue.task_done()
            if len(self.visited_urls) % batch_size == 0:
                self.flush_batch(batch)
                print(f"Crawled: {len(self.visited_urls)} pages...")

            if len(self.visited_urls) >= self.max_pages:
                stop_event.set()
                break

    def flush_batch(self, batch):
        # write all pending page info and update indexer DB (speeding up using batches)
        with self.db:
            for current_url_id, last_modified, page_title, page_size in batch:
                self.db.execute('INSERT OR REPLACE INTO id_to_last_modification_date (urlId, lastModificationDate) VALUES (?, ?)',
                                (current_url_id, last_modified))
                self.db.execute('INSERT OR REPLACE INTO id_to_page_title (urlId, pageTitle) VALUES (?, ?)',
                                (current_url_id, page_title))
                self.db.execute('INSERT OR REPLACE INTO id_to_page_size (urlId, pageSize) VALUES (?, ?)',
                                (current_url_id, page_size))
        self.indexer.updateSQLiteDB()
        batch.clear()

    # used asyncio to fasten the crawling 
    # and to avoid blocking the main thread
    # reduced the total crawling time from 214 seconds for 300 pages to 27 seconds
    # BONUS
    async def crawl_async(self, num_workers=40, batch_size=10):
        self.clear_spider_tables()
        self.visited_urls = set()
        self.enqueued_urls = set([self.start_url])
        url_queue = Queue()
        await url_queue.put((self.start_url, None))
        start_time = time.time()
        batch = []
        stop_event = asyncio.Event()
        async with aiohttp.ClientSession() as session:
            workers = [asyncio.create_task(self.worker(session, url_queue, batch, batch_size, stop_event)) for _ in range(num_workers)]
            await url_queue.join()
            stop_event.set()
            for w in workers:
                w.cancel()
            await asyncio.gather(*workers, return_exceptions=True)
        # final flush
        if batch:
            self.flush_batch(batch)
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

        end_time = time.time()
        elapsed = end_time - start_time
        print(f"Total crawling time: {elapsed:.2f} seconds")

    def crawl(self):
        asyncio.run(self.crawl_async())


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


