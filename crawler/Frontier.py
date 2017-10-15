from crawler.UrlQueue import UrlQueue


class Frontier:
    def __init__(self, seed_url, docs_bound):
        self.queue = UrlQueue()
        self.queue.add_url(seed_url)
        self.docs_bound = docs_bound
        self.cnt_added = 0

    def done(self):
        return not self.queue.has_next_site()

    def next_site(self):
        return self.queue.next_site()

    def add_url(self, url):
        if self.cnt_added < self.docs_bound*2:
            self.cnt_added += 1
            self.queue.add_url(url)
        else:
           self.queue.add_url_if_site_exists(url)

    def releaseSite(self, site):
        self.queue.release_site(site)