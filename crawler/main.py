import os

from crawler.Crawler import Crawler
from crawler.Frontier import Frontier

if __name__ == "__main__":
    dir_for_docs = 'documents'
    if not os.path.exists(dir_for_docs):
        os.mkdir(dir_for_docs)

    frontier = Frontier('https://www.palantir.com/careers/')
    crawler = Crawler(5, frontier, dir_for_docs)

    crawler.run()
