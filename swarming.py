#!/usr/bin/python3

import argparse

import json
import logging
import logging.config

from modules.logging import setupLogging
from units.core.core import Core

with open('config/log.json', 'r') as log_conf:
    json_conf = json.loads(log_conf.read())
    logging.config.dictConfig(json_conf)

parser = argparse.ArgumentParser()

parser.add_argument('-s', '--session', help='session name', nargs=1, default='default')
parser.add_argument('-l', '--log-level', choices=['debug', 'info', 'warning', 'error', 'critical'])

args = parser.parse_args()

# Set root-logger handlers log level
if args.log_level:
    rlogger = logging.getLogger()
    log_level = getattr(logging, args.log_level.upper())

    for handler in rlogger.handlers:
        handler.setLevel(log_level)

#logger = logging.getLogger('unit')
#logger.info("Error!!!!")

core = Core()
core.start()