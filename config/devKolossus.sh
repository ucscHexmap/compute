
export ADMIN_EMAIL=swat@soe.ucsc.edu
export ALLOWABLE_VIEWERS=https://hexdev.sdsc.edu:8222,https://hexdev.sdsc.edu:8229,http://hexdev.sdsc.edu:8222,https://hexdev.sdsc.edu:8229
export BACK_OR_FOREGROUND=BACK
export CA=/cluster/home/swat/kolossus_certs/chain.crt
export CERT=/cluster/home/swat/kolossus_certs/server.crt
#export CA=/cluster/home/swat/kolossus_certs/chain.crt
#export CERT=/cluster/home/swat/certs/kolossus/server.crt
export DATA_ROOT=/hive/groups/hexmap/dev/data
export DEBUG=1
export DEV=1
export DRL_PATH=/cluster/home/swat/packages/drl-graph-layout/bin
export FLASK_DEBUG=1
export HUB_PATH=/hive/groups/hexmap/dev/compute
export KEY=/cluster/home/swat/kolossus_certs/server.key
#export KEY=/cluster/home/swat/certs/kolossus/server.key
export LD_LIBRARY_PATH=$HUB_PATH/libPatchKolossus:$LD_LIBRARY_PATH
export PYENV=$HUB_PATH/../envKolossus
export TEST_DATA_ROOT=$HUB_PATH/tests/in/dataRoot
#export TETE_PATH=/cluster/home/swat/tete_copy/tete
export USE_HTTPS=1
export VIEWER_URL=https://hexdev.sdsc.edu:8222
export WWW_SOCKET=kolossus.sdsc.edu:8442

# If the python environment is present then open it up.
if [ -e $PYENV/bin/activate ]; then
    echo 'entering virtualenv:' $PYENV
    source $PYENV/bin/activate
fi
