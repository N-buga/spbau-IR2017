import os
import pickle
import sys

import multiprocessing as mp

from crawler.frontier import Frontier
from storage.inverted_index import InvertedIndex
from web_server.web_server import WebServer

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from crawler.launch import launch
from ranking.ranking import process

ctx = mp.get_context('spawn')

if __name__ == "__main__":
    dir_for_docs = 'documents'
    if not os.path.exists(dir_for_docs):
        os.mkdir(dir_for_docs)

    dir_checkpoints = 'checkpoints'
    if not os.path.exists(dir_checkpoints):
        os.mkdir(dir_checkpoints)

    checkpoints_name = 'checkpoints.save'
    descr_file = 'descr.txt'

    seeds = ['https://afisha.yandex.ru/', 'https://kudago.com']
    pages_bound = 300  # 100000
    lock = ctx.Lock()

    if checkpoints_name not in os.listdir(dir_checkpoints):
        inv_index = InvertedIndex('inv.index')
        frontier = Frontier(seeds, pages_bound)
        documents = None
        step_count = None

        print('No checkpoints were found.')
    else:
        with open(os.path.join(dir_checkpoints, checkpoints_name), 'rb') as check_file:
            crawler_loaded = pickle.load(check_file)

        if isinstance(crawler_loaded, tuple):
            frontier, documents, step_count, inv_index = crawler_loaded
        else:
            frontier = crawler_loaded.frontier
            documents = crawler_loaded.documents
            step_count = crawler_loaded.step_count
            inv_index = crawler_loaded.inv_index

        print('Found checkpoints. Loaded crawler. Count urls in queue is {}'.format(frontier.cnt_added))

    proc = ctx.Process(target=launch,
                       args=(dir_for_docs, dir_checkpoints,
                             checkpoints_name, descr_file,
                             lock, inv_index, frontier,
                             documents, step_count))

    proc.start()
    try:
        server = WebServer(lock, os.path.join(dir_checkpoints, checkpoints_name), descr_file)
        server.run_server()
        # in_ = input()
        # while in_ != 'exit':
        #     process(in_, lock, os.path.join(dir_checkpoints, checkpoints_name), descr_file)
        #     in_ = input()
    finally:
        proc.terminate()
