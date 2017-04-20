#!/bin/bash

# uwsgi.sh
# usage: uwsgi.sh <install>
# where:
#   <install> is the full path of config file for this particular install
#            in the config dir

# Run this startup script from an install-specific script similar to:
# INSTALL=dev
# WWW_PATH=/hive/groups/hexmap/dev/compute/www/
# $WWW_PATH/uwsgi.sh $INSTALL $WWW_PATH

INSTALL=$1
WWW_PATH=$2

source $WWW_PATH/config/$INSTALL.sh

if [ ${HTTP} ]; then
    echo Starting HTTP server on $INSTALL
    uwsgi \
        --master \
        --http-socket $WWW_SOCKET \
        --wsgi-file $WWW_PATH/www.py \
        --callable app \
        --processes 1 \
        --threads 1
else
    echo Starting HTTPS server on $INSTALL
    (nohup uwsgi \
        --master \
        --https-socket $WWW_SOCKET,$CERT,$KEY,HIGH,$CA \
        --wsgi-file $WWW_PATH/www.py \
        --callable app \
        --pidfile $PID_PATH \
        --processes 1 \
        --threads 1 \
        &> $WWW_PATH/../www.log &)
fi
