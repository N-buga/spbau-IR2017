from crawler.UrlQueue import UrlQueue


class Frontier:
    def __init__(self, seed_url):
        self.queue = UrlQueue()
        self.queue.add_url(seed_url)

    def done(self):
        return not self.queue.has_next_site()

    def next_site(self):
        return self.queue.next_site()

    def add_url(self, url):
        self.queue.add_url(url)

    def releaseSite(self, site):
        self.queue.release_site(site)