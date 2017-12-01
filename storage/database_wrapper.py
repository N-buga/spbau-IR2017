import config
import psycopg2


class TableWrapper:
    # Need to be overrided
    TABLE_NAME = None
    command_check_table_exists = None
    command_create_table = None

    def __init__(self):
        try:
            self.conn = psycopg2.connect('dbname=test user={} password={}'.
                                         format(config.get_user(), config.get_password()))
            self.conn.autocommit = True
        except:
            print('I am unable to connect to the database.')
            print("Index won't be creating")
            return

        cur = self.conn.cursor()
        cur.execute("""SELECT table_name FROM information_schema.tables
               WHERE table_schema = 'public'""")
        tables = cur.fetchall()

        if (self.TABLE_NAME,) not in tables:
            try:
                cur.execute(self.command_create_table)
            except Exception as err:
                print('Could not create a table {}.'.format(self.TABLE_NAME))
                print("PageFileAttribute index won't be creating")
                print(err)
                return

    def row_exists(self, url_id):
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT url_id FROM {} WHERE url_id = %s".format(self.TABLE_NAME), (url_id,))
        except Exception as err:
            print("Can't check if row exists.")
            print(err)
            return None
        return cur.fetchone() is not None

    def get_row(self, url_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM {} WHERE url_id = %s".format(self.TABLE_NAME), (url_id,))
        return cur.fetchone()

    def drop_data(self):
        cur = self.conn.cursor()
        cur.execute("truncate {};".format(self.TABLE_NAME))


class FileAttributeTableWrapper(TableWrapper):
    TABLE_NAME = "page_statistics"
    command_create_table = \
        """
        CREATE TABLE {} (
                url_id text PRIMARY KEY,
                url text NOT NULL,
                cnt_words INTEGER NOT NULL,
                cnt_unique_words INTEGER NOT NULL,
                cnt_links INTEGER NOT NULL
        )
        """.format(TABLE_NAME)

    def __init__(self):
        super().__init__()

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

    def insert_row(self, row):
        cur = self.conn.cursor()
        try:
            cur.execute("INSERT INTO {} VALUES (%s, %s, %s, %s, %s)".format(self.TABLE_NAME), row)
            return True
        except:
            return False

    def update_row(self, new_row):
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                UPDATE {} SET url_id=%s, url=%s, cnt_words=%s, cnt_unique_words=%s, cnt_links=%s
                WHERE url_id=%s
                """.format(self.TABLE_NAME), (*new_row, new_row[0])
            )
            return True
        except Exception as err:
            print("Can't update row.")
            print(err)
            return False

    def get_average(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT AVG(cnt_words)
            FROM {};
            """.format(self.TABLE_NAME)
        )
        return cur.fetchall()


class EntityTableWrapper(TableWrapper):
    TABLE_NAME = "entities"
    command_create_table = \
        """
        CREATE TABLE {} (
                url_id text PRIMARY KEY,
                url text NOT NULL,
                event_type text,
                event_time text,
                event_date text,
                price FLOAT,
                city text,
                venue text,
                event_name text
        )
        """.format(TABLE_NAME)

    def __init__(self):
        super().__init__()

    def index(self, url_id, url, db_entry):
        if_exists = self.row_exists(url_id)
        if if_exists is None:
            return False
        row = (url_id,
               url,
               db_entry.type,
               db_entry.time,
               db_entry.date,
               db_entry.price,
               db_entry.city,
               db_entry.venue,
               db_entry.name)

        if not if_exists:
            return self.insert_row(row)
        else:
            return self.update_row(row)

    def insert_row(self, row):
        cur = self.conn.cursor()
        try:
            cur.execute("INSERT INTO {} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)".format(self.TABLE_NAME), row)
            return True
        except Exception as err:
            print("Couldn't insert row {}".format(row))
            print(err)
            return False

    def update_row(self, new_row):
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                UPDATE {} SET url_id=%s, url=%s, event_type=%s, event_time=%s, event_date=%s,\
                price=%s, city=%s, venue=%s, event_name=%s
                WHERE url_id=%s
                """.format(self.TABLE_NAME), (*new_row, new_row[0])
            )
            return True
        except Exception as err:
            print("Can't update row.")
            print(err)
            return False
