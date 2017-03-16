#!/bin/bash

# uwsgi.sh
# usage: uwsgi.sh <install>
# where:
#   <install> is the full path of config file for this particular install
#            in the config dir

# Run this startup script from an install-specific script similar to:
# INSTALL=dev
# HUB_PATH=/hive/groups/hexmap/dev/compute/www/
# $HUB_PATH/uwsgi.sh $INSTALL $HUB_PATH

INSTALL=$1
HUB_PATH=$2

source $HUB_PATH/config/$INSTALL.sh

if [ ${HTTP} ]; then
    echo Starting HTTP server on $INSTALL
    uwsgi \
        --master \
        --http-socket $HUB_SOCKET \
        --wsgi-file $HUB_PATH/hub.py \
        --callable app \
        --processes 1 \
        --threads 1
else
    echo Starting HTTPS server on $INSTALL
    uwsgi \
        --master \
        --https-socket $HUB_SOCKET,$CERT,$KEY,HIGH,$CA \
        --wsgi-file $HUB_PATH/hub.py \
        --callable app \
        --pidfile $PID_PATH \
        --processes 1 \
        --threads 1
fi
