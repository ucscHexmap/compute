
export ADMIN_EMAIL=swat@soe.ucsc.edu
export ALLOWABLE_VIEWERS=https://hexdev.sdsc.edu:8222,https://hexdev.sdsc.edu:8229,http://hexdev.sdsc.edu:8222,https://hexdev.sdsc.edu:8229
export BACK_OR_FOREGROUND=BACK
export CA=/data/certs/chain.crt
export CERT=/data/certs/hexdev.crt
export DATA_ROOT=/hive/groups/hexmap/dev/data
export DEBUG=0
export DRL_PATH=/cluster/home/swat/packages/drl-graph-layout/bin
export FLASK_DEBUG=1
export HUB_PATH=/hive/groups/hexmap/dev/compute
export KEY=/data/certs/hexdev.key
export LD_LIBRARY_PATH=$HUB_PATH/libPatch:$LD_LIBRARY_PATH
export PYENV=/hive/groups/hexmap/dev/env
export TEST_DATA_ROOT=/cluster/home/dmccoll/compute-server/tests/in/dataRoot
export TETE_PATH=/cluster/home/swat/tete_copy/tete
export USE_HTTPS=1
export VIEWER_URL=https://hexdev.sdsc.edu:8222
export WWW_SOCKET=hexdev.sdsc.edu:8332

# If the python environment is present then open it up.
if [ -e $PYENV/bin/activate ]; then
    echo 'entering virtualenv'
    source $PYENV/bin/activate
fi
