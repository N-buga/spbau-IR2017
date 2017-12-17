import os
import pickle
from shutil import copyfile

import _pickle
import hashlib

from config import get_log,get_entertainments_words
from crawler.page import Page
from crawler.page import url_retriever_factory
from storage.inverted_index import Document
from storage.database_wrapper import EntityTableWrapper, FileAttributeTableWrapper
from storage.text_handling import TextUtils


class Crawler:
    USERAGENT = 'loaferspider'

    def __init__(self, frontier, dir_to_save, dir_checkpoints, checkpoints_name, lock, inv_index, file_description):
        self.dir_checkpoints = dir_checkpoints
        self.frontier = frontier
        self.dir_to_save = dir_to_save
        self.documents = {}
        self.file_description = file_description
        self.checkpoints_name = checkpoints_name
        self.steps_count = 0
        self.inv_index = inv_index
        self.enities_wrapper = EntityTableWrapper()
        self.fileattribute_wrapper = FileAttributeTableWrapper()
        self.lock = lock
        self.entertainment_words = TextUtils.handle(' '.join(get_entertainments_words()))

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
        get_log().debug('begin execute run')
        while not self.frontier.done():
            self.steps_count += 1
            website = self.frontier.next_site()
            current_url = website.next_updated_url()
            get_log().debug(self.steps_count)
            if not current_url:
                continue
            get_log().debug(current_url)
            website.read_robots_txt()
            website_delay = website.get_crawl_delay(self.USERAGENT)
            page = Page(current_url, website_delay)
            if not page.retrieve():
                self.frontier.remove_url(current_url)
                continue
            if website.permit_crawl(current_url):
                if page.allow_cache():
                    text = page.get_text()
                    if not any(word in text.lower() for word in self.entertainment_words):
                        if any(word in text.lower() for word in ['map', 'karta', 'kart']):
                            urls = page.extract_urls(current_url)
                            for url in urls:
                                self.frontier.add_url(url)
                        self.frontier.remove_url(current_url)
                        continue
                    self.store_document(current_url, text)
                    self.enities_wrapper.index(
                        self.url_id(current_url),
                        current_url,
                        url_retriever_factory(current_url, text, page.main_soup).form_db_entry()
                    )
                    self.fileattribute_wrapper.index(
                        self.url_id(current_url),
                        current_url,
                        page.soup
                    )
                urls = page.extract_urls(current_url)
                for url in urls:
                    self.frontier.add_url(url)
            if self.steps_count % 20 == 0: # 000 == 0:
                self.create_index()
            if self.steps_count % 10 == 0:  # 00 == 0:
                self.create_checkpoint()

    def store_document(self, url, text):
        path = os.path.join(self.dir_to_save, self.create_file_name(self.url_id(url)))
        with open(path, 'w', encoding='utf-8') as file_to:
            print(text, file=file_to, end='')
        self.documents[url] = path
        return True

    def create_checkpoint(self):
        try:
            byte_present = pickle.dumps((self.frontier, self.documents, self.steps_count, self.inv_index))
        except _pickle.PicklingError:
            print("Error getting pickling!")
            return
        self.lock.acquire()
        with open(os.path.join(self.dir_checkpoints, self.checkpoints_name), 'wb') as file:
            file.write(byte_present)
        self.lock.release()

        with open(self.file_description, 'w', encoding='utf-8') as descr:
            for url in self.documents:
                print('{}\t{}'.format(url, self.documents[url]), file=descr)
        copyfile(self.file_description, os.path.join(self.dir_checkpoints, self.file_description))
        print('Saved, step passed: {}, urls in queue: {}'.format(self.steps_count, self.frontier.cnt_added))

    @staticmethod
    def url_id(url):
        hash = hashlib.md5()
        hash.update(url.encode('utf-8'))
        hash_value = hash.hexdigest()
        return hash_value

    def create_index(self):
        docs = {}
        for url in self.documents:
            path = self.documents[url]
            if os.path.exists(path):
                docs[self.url_id(url)] = Document(path)
        self.inv_index.create_index(self.lock, docs)
