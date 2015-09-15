
import configparser

config = None

if not config:
    config = configparser.ConfigParser()

    config['test'] = {"test":"value"}
