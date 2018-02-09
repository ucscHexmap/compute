
export ADMIN_EMAIL=hexmap@ucsc.edu

# Which viewers are allowed to request certain data.
export ALLOWABLE_VIEWERS=https://tumormap.ucsc.edu,https://hexdev.sdsc.edu:8222,https://hexdev.sdsc.edu:8229

# Whether the server runs with nohup, or runs directly on your terminal.
#"FORE" or "BACK"
export BACK_OR_FOREGROUND=BACK

# https certificate authority chain
export CA=/cluster/home/swat/kolossus_certs/chain.crt

# https public certificate
export CERT=/cluster/home/swat/kolossus_certs/server.crt

# Points to the map data that will be served.
export DATA_ROOT=/hive/groups/hexmap/prod/data

# Logging debug level when 1, when 0 production logging level
export DEBUG=0

# Add DRL to the path.
export DRL_PATH=/cluster/home/swat/packages/drl-graph-layout/bin

# Controls amount of chatter on server output.
export FLASK_DEBUG=0

# Path to the "compute" directory
export HUB_PATH=/hive/groups/hexmap/prod/compute

# https private key
export KEY=/cluster/home/swat/kolossus_certs/server.key

# Only needed for some centos. Centos complains about missing a shared
# library when calling uwsgi. The solution is to provide sym lynks
# to make the file names conform. 
export LD_LIBRARY_PATH=$HUB_PATH/libPatchKolossus:$LD_LIBRARY_PATH

# This path has to be above/equal to your 'compute' dir in the
# file hierarchy.
export PYENV=/hive/groups/hexmap/prod/envKolossus
#export PYENV=/cluster/home/dmccoll/compute-env

# Path to the test data root. 
export TEST_DATA_ROOT=/cluster/home/dmccoll/compute-server/tests/in/dataRoot

# Define path to tete executable
export TETE_PATH=/cluster/home/swat/tete_copy/tete

# HTTPS=1 if https is desired. Otherwise server boots to HTTP.
export USE_HTTPS=1 

# Some of the tests ping the server.
export VIEWER_URL=https://tumormap.ucsc.edu

# Communication port
export WWW_SOCKET=kolossus.sdsc.edu:8332


# If the python environment is present then open it up.
if [ -e $PYENV/bin/activate ]; then
    echo 'entering virtualenv:' $PYENV
    source $PYENV/bin/activate
fi