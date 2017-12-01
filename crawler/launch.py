import os
import pickle
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from crawler.crawler import Crawler


def launch(dir_for_docs, dir_checkpoints, checkpoints_name, description_file,
           lock, inv_index, frontier, documents, step_count):
    crawler = Crawler(frontier, dir_for_docs, dir_checkpoints, checkpoints_name, lock, inv_index, description_file)
    if documents is None:
        open(crawler.file_description, 'w').close()  # Wipe file
    else:
        crawler.documents = documents
    if step_count is not None:
        crawler.steps_count = step_count

    crawler.run()
