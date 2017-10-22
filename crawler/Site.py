import socket
import urllib.robotparser as urobot
import re
# import requests
from urllib.error import URLError


class Site:
    _RESPONSE_TIMEOUT = 1

    def __init__(self, scheme, hostname):
        self.hostname = hostname
        self.iter = 0
        initial_url = scheme + '://' + self.hostname
#       self.urls = {0: self._setup_url(initial_url)}
        self.urls = {0: initial_url}
        self._rp = urobot.RobotFileParser()
        self._rp.set_url(scheme + '://' + hostname + '/robots.txt')

#    def _setup_url(self, url):
#        r = requests.get()

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
            return True
        return False

    def next_url(self):
        # updating
        self.iter = (self.iter + 1) % len(self.urls)
        return self.urls[self.iter]

    def permit_crawl(self, url):
        return self._rp.can_fetch('bot', url)

    def get_crawl_delay(self, useragent):
        try:
            return self._rp.crawl_delay(useragent)
        except AttributeError as e:
            print("[SITE -- get_crawl_delay] url: {0} AttributeError:".format(self.hostname), e)
            return None
