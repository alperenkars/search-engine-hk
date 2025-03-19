
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

class ContentExtractor:
    def __init__(self):
        pass

    def getTitle(self, page: str) -> str:
        soup = BeautifulSoup(page, 'html.parser')
        return soup.title.string if soup.title else ""

    def getBodyText(self, page: str) -> str:
        soup = BeautifulSoup(page, 'html.parser')
        body = soup.find('body')
        return body.get_text(separator=' ') if body else ""

    def splitWords(self, words: str) -> list[str]:
        splittedWords = re.split(r"[^a-zA-Z0-9'\-]+", words)
        return [i.strip('-').strip(' ') for i in splittedWords if i not in ['', '-']]

    def getLastModDate(self, headers) -> str:
        if 'Last-Modified' in headers:
            return headers['Last-Modified']
        return headers.get('Date', '')

    def getLinks(self, baseUrl: str, page: str) -> list[str]:
        soup = BeautifulSoup(page, 'html.parser')
        links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                links.append(urljoin(baseUrl, href))
        return links

    def getPagesize(self, headers, bodyText: str) -> int:
        if 'Content-Length' in headers:
            return int(headers['Content-Length'])
        return len(bodyText)