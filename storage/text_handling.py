from nltk.stem import SnowballStemmer
from nltk import word_tokenize
from nltk.corpus import stopwords
import string


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
    def extract_places(text):
        pass  # TODO using NLTK


    @staticmethod
    def stem(words, locale):
        stemmer = SnowballStemmer(locale)
        return [stemmer.stem(word) for word in words]

    @staticmethod
    def handle(text, main_locale, locales):
        return TextUtils.stem(
            TextUtils.only_words(TextUtils.filter_stop_words(
                TextUtils.text_to_words(text),
                locales=locales
            )),
            locale=main_locale
        )
