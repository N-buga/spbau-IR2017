import os

from crawler.Page import Page


class Crawler:
    def __init__(self, docs_bound, frontier, dir_to_save):
        self.docs_bound = docs_bound
        self.frontier = frontier
        self.dir_to_save = dir_to_save
        self.documents = {}

    @staticmethod
    def create_file_name(url):
        return 'document_from_url_{}'.format(str(url.split('/')))

    def run(self):
        stored_docs = 0
        while not self.frontier.done() and stored_docs < self.docs_bound:
            website = self.frontier.next_site()
            current_url = website.next_url()
            page = Page(current_url)
            page.retrieve()
            if website.permit_crawl(current_url):
                if page.allow_cache():
                    text = page.get_text()
                    if self.store_document(current_url, text):
                        stored_docs += 1
                urls = page.extract_urls(current_url)
                for url in urls[:10]: # TODO: DELETE
                    self.frontier.add_url(url)
            self.frontier.releaseSite(website)

    def store_document(self, url, text):
        path = os.path.join(self.dir_to_save, self.create_file_name(url))
        with open(path, 'w') as file_to:
            print(text, file=file_to, end='')
        self.documents[url] = path
        return True
