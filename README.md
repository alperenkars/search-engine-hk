# Web Search Engine Project

This project was developed as part of **COMP4321: Information Retrieval & Web Search** at The Hong Kong University of Science and Technology. It implements a miniature web-based search engine with a crawler, indexer, and retrieval system, complete with a user interface.

---

## Features

- **Web Crawler (Spider)**  
  - Uses a breadth-first search (BFS) strategy to recursively fetch and index pages from a given URL.  
  - Handles cyclic links and modified pages gracefully.  
  - Builds a parent/child link structure for navigation.  

- **Indexer**  
  - Extracts keywords from page titles and bodies.  
  - Removes stop words and applies Porter stemming algorithm.  
  - Creates inverted files supporting phrase queries (e.g., `"hong kong"`).  
  - Stores and manages data with **SQLite**.  

- **Retrieval (Search Engine)**  
  - Implements the **vector space model** with TF–IDF weighting.  
  - Computes cosine similarity to rank results.  
  - Prioritizes matches in page titles for more relevant results.  
  - Returns up to 50 results ranked by score.  

- **Web Interface**  
  - Query box for keyword and phrase searches.  
  - Displays results with score, title, URL, metadata (last modified, size), frequent keywords, and parent/child links.  
  - Results are hyperlinked for easy access.  

---

## Technology Stack

- **Python** (main implementation)  
- **Django** (web interface)  
- **SQLite** (database management)  
- **HTML Parser** (for page parsing)  

---

## Example Use Case

1. Provide a starting URL and number of pages to index.  
2. The crawler fetches and stores pages.  
3. Queries like `"hong kong universities"` are processed.  
4. Results are ranked and displayed on the web interface.  

---

## Project Context

This project was completed as the final assignment for **COMP4321**. It demonstrates concepts in information retrieval, web crawling, inverted indexing, and query processing, similar to the foundations of modern search engines.


# How to set up your local virtual Python environment & install all necessary packages

1. Open your Git Bash terminal and make sure you are in the project directory. Type `py -m venv venv` to create a new virtual environment called `venv`.

2. Then, activate the virtual environment by typing `source venv/Scripts/activate`. You should see `(venv)` in your command line interface if you have successfully activated the virtual environment.

3. Install all the requirements using `pip install -r requirements.txt` command. After that, you can type `pip freeze` to see what packages have been successfully installed.

---

# How to run Spider

1. After activating the virtual environment, run the Spider by entering `python Spider.py` to start the crawling process. After the crawling process is finished, you should see `main.db` is generated. This SQLite database stores all the database table files that contain the indexed 30 pages starting from `https://www.cse.ust.hk/~kwtleung/COMP4321/testpage.htm`.

2. Then, you can run the test program by entering `python generate_spider_result.py`. After a while, you should see `spider_result.txt` is generated. This txt file would contain the output of the test program.


# How to start up the Django web server & see the web user interface

## For Windows

1. After you finish running the Spider, make sure you are still located inside the `project` directory. Then, you can start the Django web server by typing `python manage.py runserver`.

2. Wait for a short while, and you should see there is a link `http://127.0.0.1:8000/` appeared in the terminal. Click on that link, or simply type in this link in your browser to go to the web user interface. (Note: You may encounter an error when you get into this link. This is due to the existence of the cookies from other groups. You can follow Step 3 below to solve this problem.)

3. To clear the previous cookies, press `F12` key to go to the Developer Tools page. Go to the `Application` tab. You should see there are 2 cookies, which are called `csrftoken` and `user_cookie_id`. Clear all these 2 cookies by clicking `Clear all cookies`. You can then refresh the web user interface by pressing `F5` key. You may also force refresh the web user interface by pressing `Shift` and `F5` keys at the same time. Alternatively, you can simply clode the browser tab, and open a new tab and serach for `http://127.0.0.1:8000/` again.

---

# What can you do with the web user interface?

## For Windows

1. You can start to start searching by typing your query in the search bar and click `Search` button. You can also perform phrase search, by using a pair of double quotation marks ("") to enclose the phrases.

2. Alternatively, you can also select a few stemmed keywords in the bottom left section and click `Search with Selected Keywords`.

3. When the web user interface returns the search result, you can click `Get Similar Pages` to search for the similar pages.

4. After you have searched for a few queries, you can see the left section would contain you latest 10 searching query history, you can click on one of it to do the query. You can also click `Clear History` to clean all query histories.

