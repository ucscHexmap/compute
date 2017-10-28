#!/bin/bash

HTTP=1
WWW_SOCKET=127.0.0.1:5000

# These don't propagate to where they're needed, so put it in login profile
#DRLPATH=/Users/swat/packages/drl-graph-layout/bin
#export PATH=$DRLPATH:$PATH
#export PYTHONPATH=$WWW_PATH:$WWW_PATH/../calc

export DATA_ROOT=/Users/swat/data/
export FLASK_DEBUG=1
export DEBUG=1
export UNIT_TEST=0
export VIEWER_URL=http://localhost:3333
export ALLOWABLE_VIEWERS=https://tumormap.ucsc.edu,https://hexdev.sdsc.edu,http://localhost:3333
export ADMIN_EMAIL=hexmap@ucsc.edu
