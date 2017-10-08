import urllib.robotparser as urobot

class Site:
    def __init__(self, hostname):
        self.hostname = hostname
        self.iter = 0
        self.urls = {0: self.hostname}
        self._rp = urobot.RobotFileParser()
        self._rp.set_url(hostname + 'robots.txt')
        self._rp.read()

    def update_urls(self, url):
        if url not in self.urls.values():
            cnt = len(self.urls)
            self.urls[cnt] = url
            return True
        return False

    def next_url(self):
        if self.iter < len(self.urls):
            self.iter += 1
            return self.urls[self.iter - 1]
        return None

    def permit_crawl(self, url):
        return self._rp.can_fetch('bot', url)
