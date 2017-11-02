import os
import pickle
from shutil import copyfile

import _pickle

from crawler.Page import Page
import hashlib

from storage.inverted_index import Document, InvertedIndex


class Crawler:
    USERAGENT = 'loaferspider'

    def __init__(self, frontier, dir_to_save, dir_checkpoints, checkpoints_name, inv_index_file_name="inv.index"):
        self.dir_checkpoints = dir_checkpoints
        self.frontier = frontier
        self.dir_to_save = dir_to_save
        self.documents = {}
        self.file_description = 'descr.txt'
        self.checkpoints_name = checkpoints_name
        self.steps_count = 0
        self.inv_index_file_name = inv_index_file_name
        self.index = None

    @staticmethod
    def create_file_name(url_hash):
        return 'document_from_url_with_hash_{}'.format(str(url_hash))

    def restore(self):
        with open(os.path.join(self.dir_checkpoints, self.file_description), 'r', encoding='utf-8') as file_descr:
            for line in file_descr:
                url, hash_value = line.strip().split('\t')
                path_to_file = os.path.join(self.dir_to_save, self.create_file_name(hash_value))
                if os.path.exists(path_to_file):
                    self.frontier.add_url(url)
                    self.steps_count += 1
                    self.documents[url] = path_to_file

    def run(self):
        while not self.frontier.done():
            self.steps_count += 1
            website = self.frontier.next_site()
            if not website.read_robots_txt():
                continue
            current_url = website.next_url()
            try:
                website_delay = website.get_crawl_delay(self.USERAGENT)
            except AttributeError as e:
                print("[CRAWLER -- run] AttributeError: ", e)
                continue
            page = Page(current_url, self.USERAGENT, website_delay)
            if not page.retrieve():
                continue
            if website.permit_crawl(current_url):
                if page.allow_cache():
                    text = page.get_text()
                    self.store_document(current_url, text)
                urls = page.extract_urls(current_url)
                for url in urls:
                    self.frontier.add_url(url)
            if self.steps_count % 100 == 0:
                self.create_checkpoint(self.steps_count)
            self.frontier.releaseSite(website)
            if self.steps_count % 10000 == 0:
                self.create_index()

    def store_document(self, url, text):
        hash = hashlib.md5()
        hash.update(url.encode('utf-8'))
        hash_value = hash.hexdigest()
        path = os.path.join(self.dir_to_save, self.create_file_name(hash_value))
        with open(path, 'w') as file_to:
            print(text, file=file_to, end='')
        self.documents[url] = path
        return True

    def create_checkpoint(self, count_passed):
        try:
            byte_present = pickle.dumps(self)
        except _pickle.PicklingError:
            print("Error getting pickling!")
            return
        with open(os.path.join(self.dir_checkpoints, self.checkpoints_name), 'wb') as file:
            file.write(byte_present)

        with open(self.file_description, 'w') as descr:
            for url in self.documents:
                print('{}\t{}'.format(url, self.documents[url]), file=descr)
        copyfile(self.file_description, os.path.join(self.dir_checkpoints, self.file_description))
        print('Saved, step passed: {}, urls in queue: {}'.format(self.steps_count, self.frontier.cnt_added))

    def create_index(self):
        docs = []
        for url in self.documents:
            path = self.documents[url]
            if os.path.exists(path):
                docs.append(Document(path))
        self.index = InvertedIndex()
        self.index.create_index(docs, self.inv_index_file_name)
