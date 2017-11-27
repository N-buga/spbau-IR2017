"""
Two-pass index
"""
import shutil
import tempfile

from storage.text_handling import TextUtils
from pyspark.sql import SparkSession


class WordDocInfo:
    def __init__(self, id, count, positions):
        self.id = id
        self.count = count
        self.positions = positions

    def add_position(self, pos):
        self.count += 1
        self.positions.append(pos)

    def serialize(self):
        return '{} {} {}\n'.format(self.id, self.count, ' '.join(map(str, self.positions)))

    @staticmethod
    def deserialize(file):
        word_doc_info = file.readline().decode('utf-8').split()
        id = word_doc_info[0]
        count = int(word_doc_info[1])
        positions = list(map(int, word_doc_info[2:]))
        return WordDocInfo(id, count, positions)


class InvertedIndex:
    def __init__(self, file_name):
        self.file_name = file_name
        self.words_begin = None
        self.partitions = 4

    def create_index(self, lock, docs):
        spark = SparkSession \
            .builder \
            .appName("InvertedIndex") \
            .getOrCreate()

        res = spark.sparkContext.parallelize(docs, self.partitions).flatMap(
            lambda doc_id: self.dict_for_doc(docs, doc_id)
        ).aggregateByKey((0, 0), self.add_doc_info, self.merge_values) \
            .map(lambda pairs_word_info: (pairs_word_info[0],
                                          (pairs_word_info[1][0] + len(
                                              '{} {}\n'.format(pairs_word_info[0], pairs_word_info[1][1]).encode(
                                                  'utf-8')),
                                           pairs_word_info[1][1])
                                          )
                 ).collect()

        word_info = dict(res)

        self.words_begin = {}
        cur_pos = 0
        for word in word_info:
            self.words_begin[word] = cur_pos
            cur_pos += word_info[word][0]

        tmp_file = tempfile.NamedTemporaryFile()
        tmp_file_name = tmp_file.name

        spark.sparkContext.parallelize(docs, self.partitions).flatMap(
            lambda doc_id: self.dict_for_doc(docs, doc_id)
        ).aggregateByKey(b'', self.add_string_doc_info, self.merge_text)\
            .map(lambda pair: (pair[0], '{} {}\n'.format(pair[0], word_info[pair[0]][1]).encode('utf-8') + pair[1]))\
            .foreach(lambda pair: self.write_to_file(pair, tmp_file_name))

        lock.acquire()
        shutil.copyfile(tmp_file_name, self.file_name)
        lock.release()

    def write_to_file(self, pair, tmp_file_name):
        word, text = pair
        file = open(tmp_file_name, 'r+b')
        file.seek(self.words_begin[word])
        file.write(text)
        file.close()

    @staticmethod
    def dict_for_doc(docs, doc_id):
        cur_words = {}
        text = docs[doc_id].get_text()
        for pos, word in enumerate(text.split()):
            if word in cur_words:
                cur_words[word].add_position(pos)
            else:
                cur_words[word] = WordDocInfo(doc_id, 1, [pos])
        return cur_words.items()

    @staticmethod
    def add_doc_info(pair, doc_info):
        size, doc_count = pair
        size += len(doc_info.serialize().encode('utf-8'))
        doc_count += 1
        return size, doc_count

    @staticmethod
    def add_string_doc_info(text, doc_info):
        serialised_info = doc_info.serialize().encode('utf-8')
        return text + serialised_info

    @staticmethod
    def merge_values(pair1, pair2):
        size = pair1[0] + pair2[0]
        doc_count = pair1[1] + pair2[1]
        return (size, doc_count)

    @staticmethod
    def merge_text(text1, text2):
        return text1 + text2

    def get_index(self, word):
        if word not in self.words_begin:
            return []
        else:
            file = open(self.file_name, 'rb')
            file.seek(self.words_begin[word])
            cnt_docs = int(file.readline().decode('utf-8').split()[1])
            info = []
            for _ in range(cnt_docs):
                info.append(WordDocInfo.deserialize(file))
            file.close()
            return info


class Document:
    def __init__(self, file_name):
        self.file_name = file_name

    def get_text(self):
        with open(self.file_name, 'rb') as file_from:
            text = file_from.read().decode('utf-8')
            return text


class TestDoc:
    def __init__(self, text):
        self.text = text

    def get_text(self):
        return self.text.split()
