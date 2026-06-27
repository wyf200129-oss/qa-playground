import configparser
import pathlib


def read(env):
    file = pathlib.Path(__file__).parents[0].resolve() / 'server_conf.ini'
    conf = configparser.ConfigParser()
    conf.read(file, encoding='utf-8')
    values = dict(conf.items(env))
    return values
