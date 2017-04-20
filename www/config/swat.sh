#!/bin/bash

DRLPATH=/Users/swat/drl/drl-graph-layout/bin
HTTP=1
WWW_SOCKET=127.0.0.1:5000

export DATA_ROOT=/Users/swat/data/
export FLASK_DEBUG=1
export DEBUG=1
export UNIT_TEST=0
export PATH=$DRLPATH:$PATH
export PYTHONPATH=$WWW_PATH:$WWW_PATH/../calc
export VIEWER_URL=http://localhost:3333
