import json
import logging
import os

logging.basicConfig(level=logging.DEBUG,
                    format='%(filename)-17s: '
                           '[%(levelname)-8s:] '
                           '%(funcName)-17s: '
                           '%(lineno)d:\t'
                           '%(message)s',
                    datefmt='%m-%d %H:%M',
                    handlers=[logging.FileHandler(filename='log.txt', mode='w', encoding='utf-8')])

log = logging.getLogger('LOGGER')
with open(os.path.join(os.path.dirname(__file__), 'db_config.json'), 'r') as config_file:
    config_info = json.load(config_file)


def get_log():
    return log


def get_password():
    return config_info['password']


def get_user():
    return config_info['user']


def get_entertainments_words():
    with open(os.path.join(os.path.dirname(__file__), 'dosug_words.txt'), 'r', encoding='utf-8') as file_from:
        return file_from.read().split()


def get_map_access_token():
    with open(os.path.join(os.path.dirname(__file__), 'map_config.json'), 'r') as f:
        info = json.load(f)
        return info['access_token']
