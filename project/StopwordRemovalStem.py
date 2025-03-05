from nltk.stem import PorterStemmer

# removing stopwords and perform stemming
class StopwordRemovalStem:

    def __init__(self):
        # use Porter's algorithm for stemming
        self.stemmer = PorterStemmer()

        # prepare the stopworddictionary
        self.stopword_list: list[str] = []
        with open('stopwords.txt') as f:
            self.stopword_list = f.read().split('\n')

    def stemming(self, words: list[str]) -> list[str]:
        return [self.stemmer.stem(w) for w in words]

    def stopwordRemoval(self, words: list[str]) -> list[str]:
        return [w for w in words if w.lower() not in self.stopword_list]
    
    # first do stopword removal, and then  do stemming
    def transform(self, words: list[str]) -> list[str]:
        
        noStopWordList = self.stopwordRemoval(words)
        transformedWordList = self.stemming(noStopWordList)

        return transformedWordList
