class Frontier:
    def __init__(self, seed_url, pages_bound):
        self.queue = UrlQueue()
        self.queue.add(seed_url)
        self.pages_bound = pages_bound
        self.cnt = 0

    def done(self):
        return self.queue.nextUrl() is None or self.cnt > self.pages_bound

    def next_site(self):
        pass

    def add_url(self):
        self.cnt += 1
        pass

    def releaseSite(self):
        pass