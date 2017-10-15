from crawler.Page import Page


class Crawler:
    USERAGENT = 'loaferspider'

    def __init__(self, frontier, dir_to_save):
        self.frontier = frontier
        self.dir_to_save = dir_to_save
        self.documents = {}

    @staticmethod
    def create_file_name(url):
        return 'document_from_url_{}'.format(url)

    def run(self):
        while not self.frontier.done():
            website = self.frontier.next_site()
            current_url = website.next_url()
            page = Page(current_url, self.USERAGENT, website.get_crawl_delay(self.USERAGENT))
            page.retrieve()
            if website.permit_crawl(current_url):
                if page.allow_cache():
                    text = page.get_text()
                    self.store_document(current_url, text)
                for url in current_url.extract_urls():
                    self.frontier.add_url(url)
            self.frontier.releaseSite(website)

    def store_document(self, url, text):
        file_name = self.create_file_name(url)
        with open(file_name, 'w') as file_to:
            print(text, file=file_to, end='')
        self.documents[url] = file_name
