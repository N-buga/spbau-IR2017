import requests
from bs4 import BeautifulSoup

class Page:
    def __init__(self, url):
        self.url = url

    def retrieve(self):
        self._page = requests.get(self.url)

    def extract_urls(self):
        result = []
        soup = BeautifulSoup(self._page, 'html.parser')
        # TODO: check if I can follow links
        for link in soup.find_all('a'):
            result.append(link.get('href'))
        return result

    def allow_cache(self):
        return True

    def allow_index(self):
        return True

    def allow_follow(self):
        return True
