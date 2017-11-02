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

# Pull in the configuration for this install
source $WWW_PATH/config/$INSTALL.sh

BASE='--master --callable app --processes 2 --threads 100 --wsgi-file '$WWW_PATH/www.py' --pidfile '$WWW_PATH/../www.pid
FOREGROUND=0

if [ $INSTALL == 'hexmap' ] || [ $INSTALL == 'hexdev' ]; then
    # use https
    SOCKET='--https-socket '$WWW_SOCKET,$CERT,$KEY,HIGH,$CA
else
    # No https
    SOCKET='--http-socket '$WWW_SOCKET
    FOREGROUND=1
fi
if [ $FOREGROUND == 1 ]; then
    uwsgi $BASE $SOCKET
else
    (nohup uwsgi $BASE $SOCKET &> $WWW_PATH/../www.log &)
fi
