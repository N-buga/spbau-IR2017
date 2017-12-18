from urllib import parse

from collections import deque
from crawler.site import Site


class UrlQueue:
    def __init__(self):
        self.sites = {}
        self.site_queue = deque()

    def add_url(self, url):
        cnt_added = 0
        row_url = url.split('?')[0]
        parsed_url = parse.urlparse(row_url)
        hostname = parsed_url.hostname
        scheme = parsed_url.scheme
        if hostname not in self.sites.keys():
            if hostname and scheme:
                site = Site(scheme, hostname)
                self.sites[hostname] = site
                self.site_queue.append(site)
                cnt_added += 1
            else:
                return False
        else:
            site = self.sites[hostname]

        if site.update_urls(row_url):
            self.site_queue.append(site)
            cnt_added += 1

        return cnt_added

    def remove_url(self, url):
        parsed_url = parse.urlparse(url)
        hostname = parsed_url.hostname
        if hostname not in self.sites.keys():
            raise AttributeError('No find hostname')
        else:
            return self.sites[hostname].remove_url(url)

    def next_site(self):
        site = self.site_queue.popleft()
        self.site_queue.append(site)
        return site

    def has_next_site(self):
        return len(self.site_queue) != 0

    def add_url_if_site_exists(self, url):
        row_url = url.split('?')[0]
        parsed_url = parse.urlparse(row_url)
        hostname = parsed_url.hostname
        if hostname in self.sites.keys():
            site = self.sites[hostname]
            result =  site.update_urls(row_url)
            if result:
                self.site_queue.append(site)
            return result
        return False
