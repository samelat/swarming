#!/bin/bash

SWARMINGS="$(ps -a | grep 'swarming.py' | cut -d ' ' -f 1)"

function join { local IFS="$1"; shift; echo "$*"; }
PIDS=$(join "," $SWARMINGS)

/usr/bin/htop -p $PIDS

