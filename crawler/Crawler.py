class Crawler:
    def __init__(self, frontier):
        self.frontier = frontier
        self.files = []

    def run(self):
        while not self.frontier.done():
            website = self.frontier.next_site()
            current_url = website.next_url()
            if website.permits_craul(current_url):
                if current_url.allow_store():
                    file = current_url.store()
                    self.files.append(file)
                for url in current_url.extract_urls():
                    self.frontier.add_url(url)
            self.frontier.releaseSite(website)
