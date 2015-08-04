#!/usr/bin/python3

import logging
import argparse

from modules.logging import setupLogging
from units.core.core import Core


parser = argparse.ArgumentParser()

parser.add_argument('-s', '--session', help='session name', nargs=1, default='default')
parser.add_argument('-l', '--log', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='set log level')

args = parser.parse_args()

setupLogging("")

root_logger = logging.getLogger('')
root_logger.setLevel(logging.DEBUG)

root_logger.debug("ALGO")

logger = logging.getLogger('user')

logger.info("Error!!!!")

#core = Core()
#core.start()