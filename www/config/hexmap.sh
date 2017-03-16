#!/bin/bash

DRLPATH=/cluster/home/hexmap/adam_novak-drl-graph-layout-c41341de8058/bin

export DATA_ROOT=/hive/groups/hexmap/prod/data/
export FLASK_DEBUG=1
export HUB_DEBUG=True
export HUB_TESTING=False
export LD_LIBRARY_PATH=$HUB_PATH/../libPatch:$LD_LIBRARY_PATH
export PATH=$DRLPATH:$PATH
export PYTHONPATH=$HUB_PATH:$HUB_PATH/../calc
export SSL_CERT=/data/certs/tumormap.crt
export SSL_KEY=/data/certs/tumormap.key
export VIEWER_URL=https://tumormap.ucsc.edu

S=/data/certs

CA=$S/chain.crt
CERT=$S/tumormap.crt
HUB_SOCKET=tumormap.ucsc.edu:8332
KEY=$S/tumormap.key
PID_PATH=$HUB_PATH/../compute.pid
