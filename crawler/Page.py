import requests
from bs4 import BeautifulSoup


class Page:
    def __init__(self, url):
        self.url = url
        self.soup = None

    def retrieve(self):
        self._page = requests.get(self.url)
        self.soup = BeautifulSoup(self._page.text, 'html.parser')

    def extract_urls(self):
        result = []
        if not self.allow_follow():
            return result
        for link in self.soup.find_all('a'):
            result.append(link.get('href'))
        return result

    def allow_cache(self):
        return self.check_permission('NOARCHIVE')

    def allow_index(self):
        return self.check_permission('NOINDEX')

    def allow_follow(self):
        return self.check_permission('NOFOLLOW')

    def check_permission(self, perm):
        for tag in self.soup.find_all('ROBOTS', 'meta'):
            if perm in tag['content'].split(', '):
                return False
        return True

    def get_text(self):
        return self._page.text
