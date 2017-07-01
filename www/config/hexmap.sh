#!/bin/bash

DRLPATH=/cluster/home/hexmap/adam_novak-drl-graph-layout-c41341de8058/bin

export DATA_ROOT=/hive/groups/hexmap/prod/data/
export FLASK_DEBUG=1
export DEBUG=1
export UNIT_TEST=0
export LD_LIBRARY_PATH=$WWW_PATH/../libPatch:$LD_LIBRARY_PATH
export PATH=$DRLPATH:$PATH
export PYTHONPATH=$WWW_PATH:$WWW_PATH/../calc
export SSL_CERT=/data/certs/tumormap.crt
export SSL_KEY=/data/certs/tumormap.key
export VIEWER_URL=https://tumormap.ucsc.edu
export ALLOWABLE_VIEWERS=https://tumormap.ucsc.edu,https://hexdev.sdsc.edu:8222

S=/data/certs

CA=$S/chain.crt
CERT=$S/tumormap.crt
WWW_SOCKET=tumormap.ucsc.edu:8332
KEY=$S/tumormap.key
PID_PATH=$WWW_PATH/../www.pid
