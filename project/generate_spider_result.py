import sqlite3

""" NOTES """
""" 
- go through the format again if it matches with the example 
"""

def generate_spider_result(db_path: str, output_file: str):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    with open(output_file, "w") as file:
        # first fetch all crawled URLs
        cursor.execute("SELECT urlId, url FROM id_to_url")
        urls = cursor.fetchall()

        for url_id, url in urls:
            # fetch page title, last modification date, and page size
            cursor.execute("SELECT pageTitle FROM id_to_page_title WHERE urlId = ?", (url_id,))
            page_title_row = cursor.fetchone()
            page_title = page_title_row[0] if page_title_row else ""

            cursor.execute("SELECT lastModificationDate FROM id_to_last_modification_date WHERE urlId = ?", (url_id,))
            last_mod_date_row = cursor.fetchone()
            last_mod_date = last_mod_date_row[0] if last_mod_date_row else ""

            cursor.execute("SELECT pageSize FROM id_to_page_size WHERE urlId = ?", (url_id,))
            page_size_row = cursor.fetchone()
            page_size = page_size_row[0] if page_size_row else ""

            # fetch keywords and their frequencies (up to 10, as specified in the handout)
            cursor.execute("SELECT value FROM forward_index WHERE urlId = ?", (url_id,))
            word_ids_row = cursor.fetchone()
            word_ids = word_ids_row[0].split()[:10] if word_ids_row else []

            keywords = []
            for word_id in word_ids:
                cursor.execute("SELECT word FROM id_to_word WHERE wordId = ?", (word_id,))
                word_row = cursor.fetchone()
                word = word_row[0] if word_row else ""

                cursor.execute("SELECT value FROM body_inverted_index WHERE wordId = ?", (word_id,))
                body_data_row = cursor.fetchone()
                body_data = body_data_row[0] if body_data_row else ""
                for entry in body_data.split():
                    entry_url_id, freq, _ = entry.split(";")
                    if entry_url_id == url_id:
                        keywords.append(f"{word} {freq}")
                        break

            # fetch child links (up to 10 again)
            cursor.execute("SELECT childrenUrlId FROM id_to_children_url_id WHERE urlId = ?", (url_id,))
            children_row = cursor.fetchone()
            child_links = []
            if children_row:
                child_ids = children_row[0].split()[:10]
                for child_id in child_ids:
                    cursor.execute("SELECT url FROM id_to_url WHERE urlId = ?", (child_id,))
                    child_url_row = cursor.fetchone()
                    child_links.append(child_url_row[0] if child_url_row else "")

            # write them all to file
            file.write(f"{page_title}\n")
            file.write(f"{url}\n")
            file.write(f"{last_mod_date}, {page_size}\n")
            file.write("; ".join(keywords) + "\n")
            file.write("\n".join(child_links) + "\n")
            file.write("-" * 30 + "\n")

    connection.close()

if __name__ == "__main__":
    db_path = "main.db"
    output_file = "spider_result.txt"
    generate_spider_result(db_path, output_file)
    print(f"Spider result written to {output_file}")