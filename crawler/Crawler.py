import os

from crawler.Page import Page


class Crawler:
    USERAGENT = 'loaferspider'

    def __init__(self, frontier, dir_to_save):
        self.frontier = frontier
        self.dir_to_save = dir_to_save
        self.documents = {}

    @staticmethod
    def create_file_name(url):
        return 'document_from_url_{}'.format(str(url.split('/')))

    def run(self):
        while not self.frontier.done():
            website = self.frontier.next_site()
            if not website.read_robots_txt():
                continue
            current_url = website.next_url()
            page = Page(current_url, self.USERAGENT, website.get_crawl_delay(self.USERAGENT))
            page.retrieve()
            if website.permit_crawl(current_url):
                if page.allow_cache():
                    text = page.get_text()
                    self.store_document(current_url, text)
                urls = page.extract_urls(current_url)
                for url in urls:
                    self.frontier.add_url(url)
            self.frontier.releaseSite(website)

    def store_document(self, url, text):
        path = os.path.join(self.dir_to_save, self.create_file_name(url))
        with open(path, 'w') as file_to:
            print(text, file=file_to, end='')
        self.documents[url] = path
        return True
