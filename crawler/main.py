import os
import sys
import pickle
from shutil import copyfile

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from crawler.Crawler import Crawler
from crawler.Frontier import Frontier

if __name__ == "__main__":
    dir_for_docs = 'documents'
    if not os.path.exists(dir_for_docs):
        os.mkdir(dir_for_docs)

    dir_checkpoints = 'checkpoints'
    if not os.path.exists(dir_checkpoints):
        os.mkdir(dir_checkpoints)

    checkpoints_name = 'checkpoints.save'
    pages_bound = 100000
    seeds = ['https://afisha.yandex.ru/', 'https://kudago.com']

    if not os.listdir(dir_checkpoints):
        print('No checkpoints were found.')
        frontier = Frontier(seeds, pages_bound)
        crawler = Crawler(frontier, dir_for_docs, dir_checkpoints, checkpoints_name)
        if os.path.exists(os.path.join(dir_checkpoints, crawler.file_description)):
            copyfile(os.path.join(dir_checkpoints, crawler.file_description), crawler.file_description)
        else:
            open(crawler.file_description, 'w').close() # Wipe file
    else:
        with open(os.path.join(dir_checkpoints, checkpoints_name), 'rb') as check_file:
            crawler_loaded = pickle.load(check_file)

        frontier = Frontier(seeds, pages_bound)
        crawler = Crawler(frontier, dir_for_docs, dir_checkpoints, checkpoints_name)

        if (crawler_loaded.__dict__.keys() == crawler.__dict__.keys()) \
                and (crawler_loaded.frontier.__dict__.keys() == crawler.frontier.__dict__.keys()):
            crawler = crawler_loaded
            print('Found checkpoints. Loaded crawler. Count urls in queue is {}'.format(crawler.frontier.cnt_added))
        else:
            print('Found checkpoints. Unable to load crawler. Load sources.')
            if os.path.exists(os.path.join(dir_checkpoints, crawler.file_description)):
                copyfile(os.path.join(dir_checkpoints, crawler.file_description), crawler.file_description)
            else:
                open(crawler.file_description, 'w').close() # Wipe file
            crawler.restore()
            print(crawler.steps_count)

    crawler.run()
