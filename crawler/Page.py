import requests
from bs4 import BeautifulSoup

from urllib.parse import urlparse, urljoin


def is_absolute(url):
    return bool(urlparse(url).netloc)


class Page:
    def __init__(self, url):
        self.url = url
        self.soup = None

    def retrieve(self):
        self._page = requests.get(self.url)
        self.soup = BeautifulSoup(self._page.text, 'html.parser')

    def extract_urls(self, current_url):
        result = []
        if not self.allow_follow():
            return result
        for html_link in self.soup.find_all('a'):
            link = html_link.get('href')
            if is_absolute(link):
                result.append(link)
            else:
                result.append(urljoin(current_url, link))
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
