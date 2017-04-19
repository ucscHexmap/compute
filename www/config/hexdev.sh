#!/bin/bash

DRLPATH=/cluster/home/swat/packages/drl-graph-layout/bin

export DATA_ROOT=/hive/groups/hexmap/dev/data/
export FLASK_DEBUG=1
export DEBUG=1
export UNIT_TEST=0
export LD_LIBRARY_PATH=$HUB_PATH/../libPatch:$LD_LIBRARY_PATH
export PATH=$DRLPATH:$PATH
export PYTHONPATH=$HUB_PATH:$HUB_PATH/../calc
export VIEWER_URL=https://hexdev.sdsc.edu:8222

S=/data/certs

CA=$S/chain.crt
CERT=$S/hexdev.crt
HUB_SOCKET=hexdev.sdsc.edu:8332
KEY=$S/hexdev.key
PID_PATH=$HUB_PATH/../compute.pid
