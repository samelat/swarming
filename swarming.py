#!/usr/bin/python3

import argparse

import modules.logging
from units.core.core import Core


parser = argparse.ArgumentParser()

parser.add_argument('-s', '--session', help='session name', nargs=1, default='default')
parser.add_argument('-l', '--log', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='set log level')

args = parser.parse_args()

#logger.critical("Error!!!!")



#core = Core()
#core.start()