
from nltk.stem.snowball import SnowballStemmer

class StopStem:  # reemove stopwords and stem the words
    def __init__(self):
        self.stopwords: list[str] = []
        with open('stopwords.txt') as f:
            self.stopwords = f.read().split('\n')
        self.stemmer = SnowballStemmer('english')

    def removeStopWords(self, words: list[str]) -> list[str]:
        return [word for word in words if word.lower() not in self.stopwords]

    def stemWords(self, words: list[str]) -> list[str]:
        return [self.stemmer.stem(word) for word in words]

    def process(self, words: list[str]) -> list[str]:
        nonStopWordList = self.removeStopWords(words)
        processedWordList = self.stemWords(nonStopWordList)
        return processedWordList