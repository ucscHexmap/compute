
export ADMIN_EMAIL=swat@soe.ucsc.edu
export ALLOWABLE_VIEWERS=http://localhost:3333,https://localhost:3333
export BACK_OR_FOREGROUND=FORE
#export CA=/data/certs/chain.crt
#export CERT=/data/certs/hexdev.crt
export DATA_ROOT=$HOME/data
export DEBUG=1
export DRL_PATH=$HOME/packages/drl-graph-layout/bin
export FLASK_DEBUG=1
export HUB_PATH=$HOME/dev/compute
#export KEY=/data/certs/hexdev.key
export PYENV=$HOME/dev/env
export TEST_DATA_ROOT=$DATA_ROOT
#export TETE_PATH=/cluster/home/swat/tete_copy/tete
export UNIT_TEST=0
export USE_HTTPS=0
export VIEWER_URL=http://localhost:3333
export WWW_SOCKET=127.0.0.1:5000

# If the python environment is present then open it up.
if [ -e $PYENV/bin/activate ]; then
    echo 'entering virtualenv:' $PYENV
    source $PYENV/bin/activate
fi
