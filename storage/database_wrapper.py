import json

import psycopg2

config_file_name = 'config.json'


class PostgresSQLWrapper:
    command_check_table_exists = 'SELECT * FROM information_schema.tables WHERE table_name=%s'
    commad_create_table = \
        """
        CREATE TABLE page_statistics (
                url_id INTEGER NOT NULL,
                url text NOT NULL,
                cnt_words INTEGER NOT NULL,
                cnt_unique_words INTEGER NOT NULL,
                cnt_links INTEGER NOT NULL,
                PRIMARY KEY url_id
        )
        """

    def __init__(self):
        config_info = json.load(config_file_name)
        self.user_name = config_info['user']
        self.password = config_info['password']
        try:
            self.conn = psycopg2.connect("dbname='metadata' user='{}' password='{}'".
                                    format(self.user_name, self.password))
        except:
            print('I am unable to connect to the database.')
            print("Index won't be creating")
            return

        cur = self.conn.cursor()
        try:
            cur.execute(self.command_check_table_exists, 'page_statistics')
        except:
            print("Couldn't check existence of table")
            print("Index won't be creating")
            return
        if cur.rowcount == 0:
            try:
                cur.execute(self.commad_create_table)
            except:
                print('Could not create a table.')
                return

    def index(self, url_id, url, soup_object):
        page_text = soup_object.get_text()
        words = page_text.split()
        words_count = len(words)
        unique_words_count = len(set(words))
        links_count = len(soup_object.find_all('a'))
        if_exists = self.row_exists(url_id)
        if if_exists is None:
            return False
        if not if_exists:
            return self.insert_row((url_id, url, words_count, unique_words_count, links_count))
        else:
            return self.update_row((url_id, url, words_count, unique_words_count, links_count))

    def row_exists(self, url_id):
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT url_id FROM page_statistics WHERE url_id = %s", (url_id,))
        except:
            print("Can't check if row exists.")
            return None
        return cur.fetchone() is not None

    def insert_row(self, row):
        cur = self.conn.cursor()
        try:
            cur.execute("INSERT INTO page_statistics VALUES (%s, %s, %s, %s, %s)", row)
            return True
        except:
            return False

    def update_row(self, new_row):
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                UPDATE page_statistics SET url_id=%s, url=%s, cnt_words=%s, cnt_unique_words=%s, cnt_links=%s)
                WHERE url_id=%s
                """, tuple(*new_row, new_row[0])
            )
            return True
        except:
            print("Can't update row.")
            return False
