import requests
import time
import re
import datetime

import dateutil.parser as dparser
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

from crawler import crawler
from storage.text_handling import TextUtils


def is_absolute(url):
    return bool(urlparse(url).netloc)


class Page:
    DEFAULT_WAIT_TIME = 0.5  # 0.5 second

    def __init__(self, url, crawl_delay=None):
        self.url = url
        self.headers = {
            'User-Agent': crawler.Crawler.USERAGENT
        }
        self.soup = None
        self.crawl_delay = crawl_delay
        self._page = None

    def retrieve(self):
        try:
            session = requests.Session()
            session.trust_env = False  # Don't read proxy settings from OS
            self._page = session.get(self.url, headers=self.headers)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError,
                requests.exceptions.InvalidSchema, requests.exceptions.ChunkedEncodingError):
            print("[PAGE -- retrieve] exception")
            return False
        time_to_wait = self.DEFAULT_WAIT_TIME
        if self.crawl_delay is not None:
            time_to_wait = self.crawl_delay
        status_code = self._page.status_code
        time.sleep(time_to_wait)

        if 400 <= status_code < 600:
            # invalidate handler value due to an error
            self.soup = None
            return False
        self.soup = BeautifulSoup(self._page.content, 'html.parser')
        return True

    def extract_urls(self, current_url):
        result = []
        if not self.allow_follow():
            return result
        for html_link in self.soup.find_all('a'):
            link = html_link.get('href')
            if is_absolute(link):
                result.append(link)
            else:
                result.append(urljoin(current_url, link))
        return result

    def allow_cache(self):
        return self.check_permission('NOARCHIVE')

    def allow_index(self):
        return self.check_permission('NOINDEX')

    def allow_follow(self):
        return self.check_permission('NOFOLLOW')

    def check_permission(self, perm):
        for tag in self.soup.find_all('ROBOTS', 'meta'):
            if perm in tag['content'].split(', '):
                return False
        return True

    def get_text(self):
        if self.soup is None:
            return ""
        strings = []
        for div in self.soup.find_all(['div', 'span', 'body']):
            strings.extend([string for string in div.stripped_strings if
                            string != "" and re.search(r'[<>{}=\[\]\|]', string) is None])
        text = "\n".join(strings)
        preprocessed_text = TextUtils.handle(text)
        return ' '.join(preprocessed_text)


def url_retriever_factory(url, bs):
    if re.match(r'.*afisha\.yandex\.ru/[a-z-]+/[a-z]+/.*', url):
        return URLYandexRetriever(url, bs)
    if re.match(r'.*mariinsky\.ru/../playbill/playbill/[0-9]+/[0-9]+/[0-9]+/[0-9]_[0-9]+', url):
        return URLMarRetriever(url, bs)
    return URLBaseRetriever(url, bs)


class DBEntry:
    def __init__(self, type, time, date, price, city, venue, name):
        self.type = type
        self.time = time
        self.date = date
        self.price = price
        self.city = city
        self.venue = venue
        self.name = name


class URLBaseRetriever:
    def __init__(self, url, soup, type=None, time=None, date=None, price=None, city=None, venue=None, name=None):
        self.url = url

        strings = []
        for div in soup.find_all(['div', 'span', 'body']):
            strings.extend([string for string in div.stripped_strings if string != "" and re.search(r'[<>{}=\[\]\|]', string) is None])

        self.time = time
        self.date = date
        if self.time is None or self.date is None:
            for s in strings:
                try:
                    d = dparser.parse(s, fuzzy=True)
                    if self.time is None:
                        self.time = str(d.time())
                    if self.date is None:
                        self.date = str(d.date())
                    break
                except:
                    continue

        self.type = type
        self.price = price
        self.city = city
        self.venue = venue

        self.name = name
        if self.name is None:
            pieces = url.split('/')
            self.name = pieces[len(pieces) - 1].split('?', 1)[0]

    def get_type(self):
        return self.type

    def get_time(self):
        return self.time

    def get_date(self):
        return self.date

    def get_price(self):
        return self.price

    def get_city(self):
        return self.city

    def get_venue(self):
        return self.venue

    def get_name(self):
        return self.name

    def form_db_entry(self):
        return DBEntry(self.get_type(), self.get_time(), self.get_date(), self.get_price(), self.get_city(), self.get_venue(), self.get_name())


class URLYandexRetriever(URLBaseRetriever):
    def __init__(self, url, soup):
        super().__init__(url, soup)

        pieces = url.split('/')
        self.type = pieces[4]
        self.city = pieces[3]

        try:
            time = soup.find_all(name='div', attrs={'class': 'event-heading__cities'})[0].text.split(':', 1)[1].split(',')
            self.date = time[0]
            self.time = time[1]
        except:
            self.date = None
            self.time = None

        try:
            self.venue = soup.find_all(name='h3', attrs={'class': 'place__title', 'itemprop': 'name'})[0].text
        except:
            self.venue = None

        try:
            self.name = soup.find_all(name='h1', attrs={'class': 'event-heading__title', 'itemprop': 'name'})[0].text
        except:
            self.name = None

        maybe_price = soup.find_all(name='span', attrs={'class': 'money_value'})
        self.price = None
        if len(maybe_price) > 0:
            self.price = maybe_price[0].text


class URLMarRetriever(URLBaseRetriever):
    def __init__(self, url, soup):
        super().__init__(url, soup, type='concert')

        pieces = url.split('/')
        self.date = datetime.date(int(pieces[6]), int(pieces[7]), int(pieces[8]))
        time = pieces[9].split('_')[1]
        hour = int(time[0:2])
        minute = int(time[2:4])
        self.time = datetime.time(hour=hour, minute=minute)

        place = soup.find_all(name='span', itemprop='location')[0].text.split(',')
        self.city = place[0]
        self.venue = place[1]
        self.name = soup.find_all(name='span', itemprop='summary')[0].text