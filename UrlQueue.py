from collections import deque
from urllib.parse import urlparse

from Site import Site


class UrlQueue:
    def __init__(self):
        self.sites = {}
        self.site_queue = deque()
        self.count_queue_urls = 0

    def add_url(self, url):
        hostname = urlparse(url).hostname
        if hostname not in self.sites.keys():
            site = Site(hostname)
            self.sites[hostname] = site
        else:
            site = self.sites[hostname]

        if site.update_urls(url):
            self.count_queue_urls += 1
            return True
        return False

    def next_site(self):
        site = self.site_queue.popleft()
        return site

    def release_site(self, site):
        self.site_queue.append(site)

    def has_next(self):
        return self.count_queue_urls != 0