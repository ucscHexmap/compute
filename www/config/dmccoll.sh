#!/bin/bash

DRLPATH=/home/duncan/hex/compute/calc/DRL_bin
HTTP=1
WWW_SOCKET=127.0.0.1:5000

export DATA_ROOT=/home/duncan/data
export FLASK_DEBUG=1
export DEBUG=1
export UNIT_TEST=0
export PATH=$DRLPATH:$PATH
export PYTHONPATH=$WWW_PATH:$WWW_PATH/../calc
export VIEWER_URL=http://localhost:3333
export ALLOWABLE_VIEWERS=https://tumormap.ucsc.edu,https://hexdev.sdsc.edu,http://localhost:3333
export ADMIN_EMAIL=hexmap@ucsc.edu
