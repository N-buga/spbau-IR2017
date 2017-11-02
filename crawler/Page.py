import requests
from bs4 import BeautifulSoup
import time

from urllib.parse import urlparse, urljoin


def is_absolute(url):
    return bool(urlparse(url).netloc)


class Page:
    DEFAULT_WAIT_TIME = 1  # 1 second

    def __init__(self, url, useragent, crawl_delay=None):
        self.url = url
        self.headers = {
            'User-Agent': useragent
        }
        self.soup = None
        self.crawl_delay = crawl_delay
        self._page = None

    def retrieve(self):
        try:
            self._page = requests.get(self.url, headers=self.headers)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError,
                requests.exceptions.InvalidSchema, requests.exceptions.ChunkedEncodingError):
            print("[PAGE -- retrieve] exception")
            return False
        time_to_wait = self.DEFAULT_WAIT_TIME
        if self.crawl_delay is not None \
                and self.DEFAULT_WAIT_TIME > self.crawl_delay:
            time_to_wait = self.crawl_delay
        status_code = self._page.status_code
        time.sleep(time_to_wait)

        if 400 <= status_code < 600:
            # invalidate handler value due to an error
            self.soup = None
            return False
        self.soup = BeautifulSoup(self._page.text, 'html.parser')
        return True

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
        return self._page.text # .get_text()
