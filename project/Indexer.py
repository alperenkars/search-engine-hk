import uuid
import sqlite3

class Indexer:

    def __init__(self):

        self.body_inverted_index = {}
        self.title_inverted_index = {}

        self.forward_index = {}

        self.word_to_id = {}
        self.id_to_word = {}

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
        
        for (word, positions) in word_position_dict.item():
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
        
        for (word, positions) in word_position_dict.item():
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
