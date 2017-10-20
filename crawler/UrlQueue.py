from urllib import parse

from collections import deque
from crawler.Site import Site


class UrlQueue:
    def __init__(self):
        self.sites = {}
        self.site_queue = deque()

    def add_url(self, url):
        parsed_url = parse.urlparse(url)
        hostname = parsed_url.hostname
        scheme = parsed_url.scheme
        if scheme is None:
            print(url)
        if hostname not in self.sites.keys():
            if hostname and scheme:
                site = Site(scheme, hostname)
                self.sites[hostname] = site
            else:
                return False
        else:
            site = self.sites[hostname]

        self.site_queue.append(site)

        return site.update_urls(url)

    def next_site(self):
        site = self.site_queue.popleft()
        self.site_queue.append(site)
        return site

    def release_site(self, site):
        self.site_queue.append(site)

    def has_next_site(self):
        return len(self.site_queue) != 0

    def add_url_if_site_exists(self, url):
        parsed_url = parse.urlparse(url)
        hostname = parsed_url.hostname
        if hostname in self.sites.keys():
            site = self.sites[hostname]
            self.site_queue.append(site)
            return site.update_urls(url)
        return False
