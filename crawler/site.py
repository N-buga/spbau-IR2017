import socket
import urllib.robotparser as urobot
import re
import requests
import requests.adapters
from requests.exceptions import ConnectionError, MissingSchema, Timeout
from urllib.error import URLError
import email.utils as eutils
import datetime

from crawler import crawler
from config import get_log

class Site:
    _RESPONSE_ROBOT_TIMEOUT = 1
    _RESPONSE_HEADER_TIMEOUT = 2

    def __init__(self, scheme, hostname):
        self.hostname = hostname
        self.iter = 0
        self.cnt_urls = {0: scheme + '://' + self.hostname}
        self.urls_cnt = {scheme + '://' + self.hostname: 0}
        self.free_numbers = set()
        self.timestamps = {0: None}
        self._rp = urobot.RobotFileParser()
        self._rp.set_url(scheme + '://' + hostname + '/robots.txt')

    @staticmethod
    def get_last_modified(url):
        try:
            session = requests.Session()
            session.trust_env = False  # Don't read proxy settings from OS
            r_headers = session.head(url, timeout=Site._RESPONSE_HEADER_TIMEOUT,
                                     headers={'User-Agent': crawler.Crawler.USERAGENT})
        except ConnectionError as err:
            get_log().error(err)
            return None
        except MissingSchema as err:
            get_log().error(err)
            return None
        except Timeout as err:
            get_log().error(err)
            return None
        except Exception as err:
            get_log().error(err)
            return None

        if 400 <= r_headers.status_code < 600 or 'Last-Modified' not in r_headers.headers:
            get_log().debug('Return code between 400 and 600 or there is no header')
            return None
        return datetime.datetime(*eutils.parsedate(r_headers.headers['Last-Modified'])[:6])

    def read_robots_txt(self):
        default_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(self._RESPONSE_ROBOT_TIMEOUT)
        try:
            self._rp.read()
            status = True
        except (URLError, ValueError) as e:
            status = False
            get_log().error(e)
        except socket.timeout as e:
            status = False
            get_log().error(e)
        finally:
            socket.setdefaulttimeout(default_timeout)
        return status

    def update_urls(self, url):
        if url[-1] == '/':
            url = url[:-1]
        pattern = re.compile('\.(css|jpg|pdf|docx|js|png|ico)$')
        if pattern.search(url.lower()):
            return False
        if url not in self.cnt_urls.values():
            if self.free_numbers:
                cnt = self.free_numbers.pop()
            else:
                cnt = len(self.cnt_urls)
            self.cnt_urls[cnt] = url
            self.urls_cnt[url] = cnt
            self.timestamps[cnt] = None
            return True
        return False

    def remove_url(self, url):
        cnt = self.urls_cnt[url]
        self.urls_cnt.pop(url, None)
        self.cnt_urls.pop(cnt, None)
        self.timestamps.pop(cnt, None)
        self.free_numbers.add(cnt)
        return True

    # returns the first url which needs update (if any) or just hasn't been inspected yet
    def next_updated_url(self):
        if len(self.cnt_urls) == 0:
            return None
        # setup
        if self.iter in self.free_numbers:
            init_iter = self.iter
            self.next_iter(init_iter) # first correct iter before init_iter or init_iter
            if self.iter == init_iter:
                return None

        init_iter = self.iter
        url = self.cnt_urls[self.iter]
        timestamp = self.timestamps[self.iter]
        last_modified = self.get_last_modified(url)

        # while we...
        #   * haven't made the whole cycle
        #   * and are sure that the page is up to date
        #     (i.e. our timestamp for it is not None and is later or equal than its last-modified header)
        # -- iterate
        while timestamp is not None and last_modified is not None \
            and timestamp >= last_modified:
            self.next_iter(init_iter)
            if self.iter == init_iter:
                break
            url = self.cnt_urls[self.iter]
            timestamp = self.timestamps[self.iter]
            last_modified = self.get_last_modified(url)
        if timestamp is not None and last_modified is not None \
            and timestamp >= last_modified:
            return None
        self.timestamps[self.iter] = last_modified
        self.iter = (self.iter + 1) % len(self.cnt_urls)
        return url

    def next_iter(self, init_iter):
        self.iter = (self.iter + 1) % len(self.cnt_urls)

        while self.iter != init_iter and self.iter in self.free_numbers:
            self.iter = (self.iter + 1) % len(self.cnt_urls)

    def permit_crawl(self, url):
        return self._rp.can_fetch('bot', url)

    def get_crawl_delay(self, useragent):
        try:
            return self._rp.crawl_delay(useragent)
        except AttributeError as e:
            get_log().error("url: {} AttributeError: {}".format(self.hostname, e))
            print(self._rp.path)
            return None
