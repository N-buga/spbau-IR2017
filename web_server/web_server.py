import asyncio
import os
import webbrowser

import websockets

from config import get_log
from ranking.ranking import process


class WebServer:
    def __init__(self, lock, path_to_checkpoints, descr_file):
        self.lock = lock
        self.descr_file = descr_file
        self.path_to_checkpoints = path_to_checkpoints

    @asyncio.coroutine
    def query_handler(self, websocket, path):
        city_query = yield from websocket.recv()
        city, query = city_query.split('\n')
        print("query:", query)

        try:
            answer = process(query, city, self.lock, self.path_to_checkpoints, self.descr_file)
        except Exception as err:
            get_log().error(err)
            print(err)
            answer = '0\n' + 'Internal error!'
        yield from websocket.send(answer)
        print("send:", answer)

    def run_server(self):
        start_server = websockets.serve(self.query_handler, 'localhost', 9999)
        asyncio.get_event_loop().run_until_complete(start_server)

        filename = os.path.join(os.path.dirname(__file__), 'serp.html')

        webbrowser.open_new_tab('file://' + os.path.realpath(filename))

        try:
            asyncio.get_event_loop().run_forever()
        except:
            pass