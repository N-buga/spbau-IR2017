import urllib.robotparser as urobot


class Site:
    def __init__(self, scheme, hostname):
        self.hostname = hostname
        self.iter = 0
        self.urls = {0: scheme + '://' + self.hostname}
        self._rp = urobot.RobotFileParser()
        self._rp.set_url(scheme + '://' + hostname + '/robots.txt')
        self._rp.read()

    def update_urls(self, url):
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
        return self._rp.crawl_delay(useragent)
