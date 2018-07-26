
export ADMIN_EMAIL=swat@soe.ucsc.edu
export BACK_OR_FOREGROUND=BACK
export CA=/data/certs/chain.crt
export CERT=/data/certs/hexdev.crt
export DATA_ROOT=/hive/groups/hexmap/dev/data
export DEBUG=1
export DEV=1
export DRLPATH=/cluster/home/swat/packages/drl-graph-layout/bin
export FLASK_DEBUG=1
export KEY=/data/certs/hexdev.key
export LD_LIBRARY_PATH=$HEXCALC/libPatchHexdev:$LD_LIBRARY_PATH
export PYENV=/hive/groups/hexmap/dev/envHexdev
export TEST_DATA_ROOT=/cluster/home/dmccoll/compute-server/tests/in/dataRoot
export TETE_PATH=/cluster/home/swat/tete_copy/tete
export USE_HTTPS=1
export VIEWER_URL=https://hexdev.sdsc.edu:8222
export WWW_SOCKET=hexdev.sdsc.edu:8332
export DATA_HOST_PORT=$WWW_SOCKET

# If the python environment is present then open it up.
if [ -e $PYENV/bin/activate ]; then
    echo 'entering virtualenv:' $PYENV
    source $PYENV/bin/activate
fi

