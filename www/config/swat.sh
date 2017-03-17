#!/bin/bash

DRLPATH=/Users/swat/drl/drl-graph-layout/bin
HTTP=1
HUB_SOCKET=127.0.0.1:5000

export DATA_ROOT=/Users/swat/data/
export FLASK_DEBUG=1
export HUB_DEBUG=True
export HUB_TESTING=False
export PATH=$DRLPATH:$PATH
export PYTHONPATH=$HUB_PATH:$HUB_PATH/../calc
export VIEWER_URL=http://localhost:3333
