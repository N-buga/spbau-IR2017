from UrlQueue import UrlQueue


class Frontier:
    def __init__(self, seed_url, pages_bound):
        self.queue = UrlQueue()
        self.queue.add_url(seed_url)
        self.pages_bound = pages_bound
        self.cnt = 0

    def done(self):
        return self.queue.has_next() is None or self.cnt > self.pages_bound

    def next_site(self):
        return self.queue.next_site()

    def add_url(self, url):
        self.cnt += 1
        self.queue.add_url(url)

    def releaseSite(self, site):
        self.queue.release_site(site)