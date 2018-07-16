
ROOT=/data
CERTS=$ROOT/certs

export ADMIN_EMAIL=hexmap@ucsc.edu

# Whether the server runs with nohup, or runs directly on your terminal.
#"FORE" or "BACK"
export BACK_OR_FOREGROUND=BACK

# https certificate authority chain
export CA=$CERTS/chain.crt

# https public certificate
export CERT=$CERTS/server.crt

# Points to the map data that will be served.
export DATA_ROOT=$ROOT/data

# Logging debug level when 1, when 0 production logging level
export DEBUG=0

# Add DRL to the path.
export DRL_PATH=$ROOT/packages/drl-graph-layout/bin

# Controls amount of chatter on server output.
export FLASK_DEBUG=0

# Username for checking existence of server processes.
export HEX_UID=hexmap

# User group to own server processes on protected ports.
export HEX_GID=protein

# Path to the install tar file.
export INSTALL_TAR_PATH=/data/home/swat/dev/compute/ops/install.tgz

# https private key
export KEY=$CERTS/server.key

# Only needed for some centos. Centos complains about missing a shared
# library when calling uwsgi. The solution is to provide sym lynks
# to make the file names conform. 
#export LD_LIBRARY_PATH=

# Port on which the server will listen.
export PORT=443

# This path needs to be above/equal to your 'compute' dir in the
# file hierarchy.
export PYENV=$HEXCALC/../env

# Path to the test data root. 
export TEST_DATA_ROOT=$HEXCALC/tests/in/dataRoot

# HTTPS=1 if https is desired. Otherwise server boots to HTTP.
export USE_HTTPS=1 

# View servers allowed to edit maps.
export VIEW_SERVER_ADDRS=132.249.245.115

# Bookmarks are created by this view server.
export VIEWER_URL=https://tumormap.ucsc.edu

# Communication port.
export WWW_SOCKET=hexcalc.ucsc.edu:$PORT


# If the python environment is present then open it up.
if [ -e $PYENV/bin/activate ]; then
    source $PYENV/bin/activate
fi
