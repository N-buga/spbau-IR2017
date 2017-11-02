"""
Two-pass index
"""
from copy import copy

from storage.text_handling import TextUtils


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
        id = int(word_doc_info[0])
        count = int(word_doc_info[1])
        positions = list(map(int, word_doc_info[2:]))
        return WordDocInfo(id, count, positions)


class InvertedIndex:
    def __init__(self):
        self.file_name = None
        self.words_begin = None

    def create_index(self, docs, file_name='inverted_index.txt'):
        self.file_name = file_name
        words_size = {}
        words_doc_count = {}
        for doc_id in docs:
            cur_words = {}
            text = docs[doc_id].get_text()
            for pos, word in enumerate(text):
                if word in cur_words:
                    cur_words[word].add_position(pos)
                else:
                    cur_words[word] = WordDocInfo(doc_id, 1, [pos])
            for word in cur_words:
                if word not in words_size:
                    words_size[word] = len('{}\n'.format(word).encode('utf-8'))
                if word not in words_doc_count:
                    words_doc_count[word] = 0
                words_size[word] += len(cur_words[word].serialize().encode('utf-8'))
                words_doc_count[word] += 1
        self.words_begin = {}
        cur_pos = 0
        for word in words_size:
            self.words_begin[word] = cur_pos
            cur_pos += words_size[word]

        cur_words_begin = copy(self.words_begin)
        open(self.file_name, 'w').close() # Create if didn't exist & wipe
        for word in cur_words_begin:
            file = open(self.file_name, 'r+b')
            file.seek(cur_words_begin[word])
            file.write('{} {}\n'.format(word, words_doc_count[word]).encode('utf-8'))
            file.close()
            cur_words_begin[word] += len('{} {}\n'.format(word, words_doc_count[word]).encode('utf-8'))

        for doc_id in docs:
            cur_words = {}
            text = docs[doc_id].get_text()
            for pos, word in enumerate(text):
                if word in cur_words:
                    cur_words[word].add_position(pos)
                else:
                    cur_words[word] = WordDocInfo(doc_id, 1, [pos])
            for word in cur_words:
                file = open(self.file_name, 'r+b')
                file.seek(cur_words_begin[word])
                serialised_info = cur_words[word].serialize()
                file.write(serialised_info.encode('utf-8'))
                cur_words_begin[word] += len(serialised_info.encode('utf-8'))

    def get_index(self, word):
        if word not in self.words_begin:
            return None
        else:
            file = open(self.file_name, 'rb')
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
            text = file_from.read()
            return TextUtils.handle(text, main_locale='russian', locales=['russian', 'english'])


class TestDoc:
    def __init__(self, text):
        self.text = text

    def get_text(self):
        return self.text.split()

# if __name__ == "__main__":
#     docs = {0: TestDoc('mama Ama mama mama bu'), 1: TestDoc('Ama тут тут bu'), 2: TestDoc('тут mama щз'),
#             3: TestDoc('nen тут тут nen'), 4: TestDoc('mama')}
#
#     ii = InvertedIndex(docs)
#     index = ii.get_index('mama')
#     for doc_info in index:
#         print(doc_info.id, doc_info.count, doc_info.positions)
