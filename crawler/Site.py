import socket
import urllib.robotparser as urobot
import re
import requests
from urllib.error import URLError
import email.utils as eutils
import datetime


class Site:
    _RESPONSE_TIMEOUT = 1

    def __init__(self, scheme, hostname):
        self.hostname = hostname
        self.iter = 0
        self.urls = {0: scheme + '://' + self.hostname}
        self.timestamps = {0: None}
        self._rp = urobot.RobotFileParser()
        self._rp.set_url(scheme + '://' + hostname + '/robots.txt')

    @staticmethod
    def get_last_modified(url):
        try:
            r = requests.get(url)
        except ConnectionError as err:
            print("[SITE -- read_robots_txt] ConnectionError")
            return None
        if 400 <= r.status_code < 600 or 'Last-Modified' not in r.headers:
            return None
        return datetime.datetime(*eutils.parsedate(r.headers['Last-Modified'])[:6])

    def read_robots_txt(self):
        default_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(self._RESPONSE_TIMEOUT)
        try:
            self._rp.read()
            status = True
        except (URLError, ValueError) as e:
            status = False
            print("[SITE -- read_robots_txt] URL- or ValueError: ", e)
        except socket.timeout:
            status = False
            print("[SITE -- read_robots_txt] socket.timeout")
        finally:
            socket.setdefaulttimeout(default_timeout)
        return status

    def update_urls(self, url):
        if url[-1] == '/':
            url = url[:-1]
        pattern = re.compile('\.(css|jpg|pdf|docx|js|png|ico)$')
        if pattern.search(url):
            return False
        if url not in self.urls.values():
            cnt = len(self.urls)
            self.urls[cnt] = url
            self.timestamps[cnt] = None
            return True
        return False

    # returns the first url which needs update (if any) or just hasn't been inspected yet
    def next_url(self):
        # setup
        init_iter = self.iter
        self.iter = (self.iter + 1) % len(self.urls)
        url = self.urls[self.iter]
        timestamp = self.timestamps[self.iter]
        last_modified = self.get_last_modified(url)

        # while we...
        #   * haven't made the whole cycle
        #   * and are sure that the page is up to date
        #     (i.e. our timestamp for it is not None and is later or equal than its last-modified header)
        # -- iterate
        while self.iter != init_iter \
            and timestamp is not None and last_modified is not None \
            and timestamp >= last_modified:
            self.iter = (self.iter + 1) % len(self.urls)
            url = self.urls[self.iter]
            timestamp = self.timestamps[self.iter]
            last_modified = self.get_last_modified(url)
        return url

    def permit_crawl(self, url):
        return self._rp.can_fetch('bot', url)

    def get_crawl_delay(self, useragent):
        try:
            return self._rp.crawl_delay(useragent)
        except AttributeError as e:
            print("[SITE -- get_crawl_delay] url: {0} AttributeError:".format(self.hostname), e)
            return None
