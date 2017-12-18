from nltk.stem import SnowballStemmer
from nltk import word_tokenize
from nltk.corpus import stopwords
import string
import re


class TextUtils: # TODO: cool name
    @staticmethod
    def text_to_words(text):
        return word_tokenize(text.translate(str.maketrans("", "", "()!@#$%^&*_+=?<>~`',…©»")))

    @staticmethod
    def filter_stop_words(words, locales):
        current_words = words
        for locale in locales:
            current_words = [word for word in current_words if word not in stopwords.words(locale)]
        return current_words

    @staticmethod
    def only_words(words):
        return [word for word in words
                if word != "" and
                word[0] not in string.digits and
                word[0] not in string.punctuation]

    @staticmethod
    def stem(words, locale='russian'):
        stemmer = SnowballStemmer(locale)
        return [stemmer.stem(word) for word in words]

    @staticmethod
    def handle(text, main_locale='russian', locales=['russian', 'english']):
        return TextUtils.stem(
            TextUtils.only_words(TextUtils.filter_stop_words(
                TextUtils.text_to_words(text),
                locales=locales
            )),
            locale=main_locale
        )

    @staticmethod
    def search(target, only_words, preprocessed_text, context=6):
        # also we get rid of the punctuation

        # words = re.findall(r'\w+', ' '.join(preprocessed_text))

        matches = (i for (i, w) in enumerate(preprocessed_text) if w.lower() == target)
        for index in matches:
            if index < context //2:
                return only_words[0:context+1], index
            elif index > len(only_words) - context//2 - 1:
                return only_words[-(context+1):], index - (context + 1)
            else:
                return only_words[index - context//2:index + context//2 + 1], context//2
        return [], 0
