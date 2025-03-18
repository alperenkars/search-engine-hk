import uuid
import sqlite3

class Indexer:

    # Initialization

    def __init__(self):

        self.body_inverted_index = {}
        self.title_inverted_index = {}

        self.forward_index = {}

        self.word_to_id = {}
        self.id_to_word = {}

        # for sqlite3 database
        self.connection = None
        self.cursor = None
        self.prepareSQLiteDB()


    # Indexer core functions
    
    def buildBodyInvertedIndex(self, words: list[str], url_id: str) -> None:
        # format is as follows:
        # {word1: [position1, position2, ...], word2: [position1, position2, ...], ...}
        word_position_dict = {}

        for (i, word) in enumerate(words):
            # if word_position_dict already contain the word
            # simply append it to the end of the corresponding value
            if word_position_dict.get(word, None) is not None:
                word_position_dict[word] += [i]
            # otherwise, create a new entry with current position i
            else:
                word_position_dict[word] = [i]
        
        for (word, positions) in word_position_dict.items():
            word_id: str = self.word_to_id[word]

            # if body_inverted_index already contain the url ID
            # simply add the corresponding frequency and positions
            if self.body_inverted_index.get(word_id, None) is not None:
                self.body_inverted_index[word_id][url_id] = {
                                                                "frequency": len(positions), 
                                                                "positions": positions
                                                            }
            # otherwise, create a new url ID in body_inverted_index first
            # then add the corresponding frequency and positions
            else:
                self.body_inverted_index[word_id] = {url_id:
                                                        {
                                                            "frequency": len(positions),
                                                            "positions": positions
                                                        }
                                                    }
                
    def buildTitleInvertedIndex(self, words: list[str], url_id: str) -> None:
        # format is as follows:
        # {word1: [position1, position2, ...], word2: [position1, position2, ...], ...}
        word_position_dict = {}

        for (i, word) in enumerate(words):
            # if word_position_dict already contain the word
            # simply append it to the end of the corresponding value
            if word_position_dict.get(word, None) is not None:
                word_position_dict[word] += [i]
            # otherwise, create a new entry with current position i
            else:
                word_position_dict[word] = [i]
        
        for (word, positions) in word_position_dict.items():
            word_id: str = self.word_to_id[word]

            # if title_inverted_index already contain the url ID
            # simply add the corresponding frequency and positions
            if self.title_inverted_index.get(word_id, None) is not None:
                self.title_inverted_index[word_id][url_id] = {
                                                                "frequency": len(positions), 
                                                                "positions": positions
                                                             }
            # otherwise, create a new url ID in title_inverted_index first
            # then add the corresponding frequency and positions
            else:
                self.title_inverted_index[word_id] = {url_id:
                                                        {
                                                            "frequency": len(positions),
                                                            "positions": positions
                                                        }
                                                     }
    
    def buildForwardIndex(self, words: list[str], url_id: str, remove_old_content: bool = False) -> None:
        # unique_words_list stores a list of unique words
        unique_words_list: list[str] = list(set(words))

        # word_ids_list stores a list of word IDs
        word_ids_list: list[str] = []

        # if we do NOT need to remove the old content
        # simply get the corresponding word IDs (store in a list) with the given URL id
        #  and assign it to word_ids_list
        if remove_old_content is False:
            word_ids_list: list[str] = self.forward_index.get(url_id, [])

        # iterate all unique words
        for word in unique_words_list:
            # get the corresponding ID of each unique word
            word_id = self.word_to_id[word]

            # append the corresponding word ID to word_ids_list if not yet put inside
            if word_id not in word_ids_list:
                word_ids_list += [word_id]
        
        # build the forward index for the given URL ID
        self.forward_index[url_id] = word_ids_list

    def addNewWord(self, words: list[str]) -> None:
        # if a word is not appeared in word_to_id
        # generate a new uuid
        # add corresponding word id to word_to_id
        # add corresponding word to id_to_word
        for word in words:
            if self.word_to_id.get(word, None) is None:
                new_id = uuid.uuid4()
                word_id: str = str(int(new_id))

                self.word_to_id[word] = word_id
                self.id_to_word[word_id] = word
    

    # SQLite database functions

    def prepareSQLiteDB(self) -> None:
        self.connection = sqlite3.connect("main.db")
        self.cursor = self.connection.cursor()


        # if the table `body_inverted_index` not exist, create it first
        if self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='body_inverted_index';").fetchone() is None:
            self.cursor.execute(f"CREATE TABLE body_inverted_index(wordId, value);")
        # otherwise, retrieve all data from the DB table and put it in `self.body_inverted_index`
        else:
            result = self.cursor.execute(f"SELECT * FROM body_inverted_index;").fetchall()
            for (wordId, value) in result:
                current_row_value = {}

                entries = value.split(" ")
                for entry in entries:
                    parts = entry.split(";")

                    url_id = parts[0]
                    word_frequency = parts[1]
                    positions = list(map(int, parts[2].split(",")))

                    current_row_value[url_id] = {
                        "frequency": word_frequency,
                        "positions": positions
                    }
                
                self.body_inverted_index[wordId] = current_row_value
        
        # if the table `title_inverted_index` not exist, create it first
        if self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='title_inverted_index';").fetchone() is None:
            self.cursor.execute(f"CREATE TABLE title_inverted_index(wordId, value);")
        # otherwise, retrieve all data from the DB table and put it in `self.title_inverted_index`
        else:
            result = self.cursor.execute(f"SELECT * FROM title_inverted_index;").fetchall()
            for (wordId, value) in result:
                current_row_value = {}

                entries = value.split(" ")
                for entry in entries:
                    parts = entry.split(";")

                    url_id = parts[0]
                    word_frequency = parts[1]
                    positions = list(map(int, parts[2].split(",")))

                    current_row_value[url_id] = {
                        "frequency": word_frequency,
                        "positions": positions
                    }
                
                self.title_inverted_index[wordId] = current_row_value


        # if the table `forward_index` not exist, create it first
        if self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='forward_index';").fetchone() is None:
            self.cursor.execute(f"CREATE TABLE forward_index(urlId, value);")
        # otherwise, retrieve all data from the DB table and put it in `self.forward_index`
        else:
            result = self.cursor.execute(f"SELECT * FROM forward_index;").fetchall()
            for row in result:
                url_id = row[0]
                value = row[1].split(" ")
                self.forward_index[url_id] = value


        # if the table `word_to_id` not exist, create it first
        if self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='word_to_id';").fetchone() is None:
            self.cursor.execute(f"CREATE TABLE word_to_id(word, wordId);")
        # otherwise, retrieve all data from the DB table and put it in `self.word_to_id`
        else:
            result = self.cursor.execute(f"SELECT * FROM word_to_id;").fetchall()
            for row in result:
                word = row[0]
                word_id = row[1]
                self.word_to_id[word] = word_id
        
        # if the table `id_to_word` not exist, create it first
        if self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='id_to_word';").fetchone() is None:
            self.cursor.execute(f"CREATE TABLE id_to_word(wordId, word);")
        # otherwise, retrieve all data from the DB table and put it in `self.id_to_word`
        else:
            result = self.cursor.execute(f"SELECT * FROM id_to_word;").fetchall()
            for row in result:
                word_id = row[0]
                word = row[1]
                self.id_to_word[word_id] = word
        
        # commit the transaction done above
        self.connection.commit()
    
    def updateSQLiteDB(self) -> None:
        
        # body & title inverted index

        # remove all data in the database table `body_inverted_index` first
        # re-create the empty database table `body_inverted_index`
        # update all the data in the table
        # commit the transaction
        self.cursor.execute(f"DROP TABLE body_inverted_index;")
        self.cursor.execute(f"CREATE TABLE body_inverted_index(wordId, value);")

        body_inverted_index_key_value_list = []
        for (key, value) in self.body_inverted_index.items():
            formatted_entries = []

            for (url_id, inner_value) in value.items():
                # value format: urlId1;frequency1;position1 urlId2;frequency2;position2,position3,position4 ...
                positions = ",".join(map(str, inner_value["positions"]))
                formatted_entry = f"{url_id};{inner_value["frequency"]};{positions}"
                formatted_entries += [formatted_entry]
            
            # join all formatted entries into a single string separated by spaces
            combined_value = " ".join(formatted_entries)

            # append the tuple (key, combined_value) to the list
            body_inverted_index_key_value_list += [(key, combined_value)]

        self.cursor.executemany(f"INSERT INTO body_inverted_index VALUES(?, ?);", body_inverted_index_key_value_list)
        self.connection.commit()

        # remove all data in the database table `title_inverted_index` first
        # re-create the empty database table `title_inverted_index`
        # update all the data in the table
        # commit the transaction
        self.cursor.execute(f"DROP TABLE title_inverted_index;")
        self.cursor.execute(f"CREATE TABLE title_inverted_index(wordId, value);")

        title_inverted_index_key_value_list = []
        for (key, value) in self.title_inverted_index.items():
            formatted_entries = []

            for (url_id, inner_value) in value.items():
                # value format: urlId1;frequency1;position1 urlId2;frequency2;position2,position3,position4 ...
                positions = ",".join(map(str, inner_value["positions"]))
                formatted_entry = f"{url_id};{inner_value["frequency"]};{positions}"
                formatted_entries += [formatted_entry]
            
            # join all formatted entries into a single string separated by spaces
            combined_value = " ".join(formatted_entries)

            # append the tuple (key, combined_value) to the list
            title_inverted_index_key_value_list += [(key, combined_value)]

        self.cursor.executemany(f"INSERT INTO title_inverted_index VALUES(?, ?);", title_inverted_index_key_value_list)
        self.connection.commit()


        # forward index

        # remove all data in the database table `forward_index` first
        # re-create the empty database table `forward_index`
        # update all the data in the table
        # commit the transaction
        self.cursor.execute(f"DROP TABLE forward_index;")
        self.cursor.execute(f"CREATE TABLE forward_index(urlId, value);")

        forward_index_key_value_list = []
        for (key, value) in self.forward_index.items():
            # Join the list of values with space into a single string
            # joined_value format: wordId1 wordId2 wordId3 ...
            joined_value = " ".join(value)
            forward_index_key_value_list += [(key, joined_value)]

        self.cursor.executemany(f"INSERT INTO forward_index VALUES(?, ?);", forward_index_key_value_list)
        self.connection.commit()


        # word <-> word_id conversion

        # remove all data in the database table `word_to_id` first
        # re-create the empty database table `word_to_id`
        # update all the data in the table
        # commit the transaction
        self.cursor.execute(f"DROP TABLE word_to_id;")
        self.cursor.execute(f"CREATE TABLE word_to_id(word, wordId);")
        self.cursor.executemany(f"INSERT INTO word_to_id VALUES(?, ?);", list(self.word_to_id.items()))
        self.connection.commit()

        # remove all data in the database table `id_to_word` first
        # re-create the empty database table `id_to_word`
        # update all the data in the table
        # commit the transaction
        self.cursor.execute(f"DROP TABLE id_to_word;")
        self.cursor.execute(f"CREATE TABLE id_to_word(wordId, word);")
        self.cursor.executemany(f"INSERT INTO id_to_word VALUES(?, ?);", list(self.id_to_word.items()))
        self.connection.commit()





        
