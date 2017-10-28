#!/bin/bash

DRLPATH=/data/packages/adam_novak-drl-graph-layout-c41341de8058/bin

export DATA_ROOT=/data/data
export FLASK_DEBUG=1
export DEBUG=1
export UNIT_TEST=0
export LD_LIBRARY_PATH=$WWW_PATH/../libPatch:$LD_LIBRARY_PATH
export PATH=$DRLPATH:$PATH
export PYTHONPATH=$WWW_PATH:$WWW_PATH/../calc
export VIEWER_URL=https://hexdev.sdsc.edu:8222
export ALLOWABLE_VIEWERS=https://hexdev.sdsc.edu:8221,https://hexdev.sdsc.edu:8222,https://hexdev.sdsc.edu:8223,http://hexdev.sdsc.edu:8221,http://hexdev.sdsc.edu:8222,http://hexdev.sdsc.edu:8223
export ADMIN_EMAIL=hexmap@ucsc.edu

S=/data/certs/cellAtlas

CA=$S/chain.crt
CERT=$S/cellatlas.crt
WWW_SOCKET=swat-calc:8332
KEY=$S/cellatlas.key
PID_PATH=$WWW_PATH/../www.pid