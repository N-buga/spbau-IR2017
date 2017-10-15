import requests
from bs4 import BeautifulSoup
import time


class Page:
    def __init__(self, url, crawl_delay=None):
        self.url = url
        self.headers = {
            'User-Agent': 'loaferspider'
        }
        self.soup = None
        self.crawl_delay = crawl_delay

    def retrieve(self):
        initial_time = time.time()
        self._page = requests.get(self.url, headers=self.headers)
        time_to_wait = initial_time - time.time()
        if self.crawl_delay is not None and time_to_wait > self.crawl_delay:
            time_to_wait = self.crawl_delay
        status_code = self._page.status_code
        time.sleep(10 * time_to_wait)

        if 400 <= status_code < 600:
            # to make sure that we do not fetch anything
            # from a previous site as from this one
            self.Soup = None
            return False
        self.soup = BeautifulSoup(self._page.text, 'html.parser')
        return True

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
        for tag in self.soup.find_all('meta', name='ROBOTS'):
            if perm in tag['content'].split(', '):
                return False
        return True

    def get_text(self):
        return self._page.text
