export ADMIN_EMAIL=hexmap@ucsc.edu

# Which viewers are allowed to request certain data.
export ALLOWABLE_VIEWERS=https://hexdev.sdsc.edu:8221,https://hexdev.sdsc.edu:8222,https://hexdev.sdsc.edu:8223,https://hexdev.sdsc.edu:8229,http://hexdev.sdsc.edu:8221,http://hexdev.sdsc.edu:8222,http://hexdev.sdsc.edu:8223,https://hexdev.sdsc.edu:8229

# Whether the server runs with nohup, or runs directly on your terminal.
#"FORE" or "BACK"
export BACK_OR_FOREGROUND=BACK

# Needed to set up virtualenv 
export BASE_PYTHONPATH=/cluster/home/dmccoll/localpy/Python-2.7.11/python 

export CA=/data/certs/chain.crt #Needed for https
export CERT=/data/certs/hexdev.crt #Needed for https

# Points to the map data that will be served.
export DATA_ROOT=/hive/groups/hexmap/dev/data

export DEBUG=0

# Add DRL to the path.
export DRL_PATH=/cluster/home/swat/packages/drl-graph-layout/bin
export PATH=$DRLPATH:$PATH

# Controls amount of chatter on server output.
export FLASK_DEBUG=1

export HUB_DBPATH=
# Path to the "compute" directory
export HUB_PATH=/hive/groups/hexmap/dev/compute
export KEY=/data/certs/hexdev.key #Needed for https

# Only needed for centos. Centos complains about missing a shared
# library when calling uwsgi. The solution is to provide sym lynks
# to make the file names conform. 
export LD_LIBRARY_PATH=$HUB_PATH/libPatch:$LD_LIBRARY_PATH

# This path has to be above/equal to your 'compute' dir in the
# file hierarchy.
export PYENV=/hive/groups/hexmap/dev/env

# Path to the test data root. 
export TEST_DATA_ROOT=/cluster/home/dmccoll/compute-server/tests/in/dataRoot

# Add tete to the pythonpath
export TETE_PATH=/cluster/home/swat/tete_copy/tete
export PYTHONPATH=$TETE_PATH:$PYTHONPATH

# HTTPS=1 if https is desired. Otherwise server boots to HTTP.
export USE_HTTPS=1 

# Some of the tests ping the server.
export VIEWER_URL=https://hexdev.sdsc.edu:8222

export WWW_PATH=$HUB_PATH/www
export WWW_SOCKET=hexdev.sdsc.edu:8332


# If the python environment is present then open it up.
if [ -e $PYENV/bin/activate ]; then
    source $PYENV/bin/activate
fi
