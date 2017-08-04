#!/bin/bash

DRLPATH=/cluster/home/swat/packages/drl-graph-layout/bin

export DATA_ROOT=/hive/groups/hexmap/dev/data/
export FLASK_DEBUG=1
export DEBUG=1
export UNIT_TEST=0
export LD_LIBRARY_PATH=$WWW_PATH/../libPatch:$LD_LIBRARY_PATH
export PATH=$DRLPATH:$PATH
export PYTHONPATH=$WWW_PATH:$WWW_PATH/../calc
export VIEWER_URL=https://hexdev.sdsc.edu:8222
export ALLOWABLE_VIEWERS=https://hexdev.sdsc.edu:8221,https://hexdev.sdsc.edu:8222,https://hexdev.sdsc.edu:8223,http://hexdev.sdsc.edu:8221,http://hexdev.sdsc.edu:8222,http://hexdev.sdsc.edu:8223
export ADMIN_EMAIL=hexmap@ucsc.edu

S=/data/certs

CA=$S/chain.crt
CERT=$S/hexdev.crt
WWW_SOCKET=hexdev.sdsc.edu:8332
KEY=$S/hexdev.key
PID_PATH=$WWW_PATH/../www.pid
