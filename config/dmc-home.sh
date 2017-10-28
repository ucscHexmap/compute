
export ADMIN_EMAIL=dmccoll@ucsc.edu
export ALLOWABLE_VIEWERS=https://tumormap.ucsc.edu,https://hexdev.sdsc.edu,http://localhost:3333
export BACK_OR_FOREGROUND=FORE #"FORE" or "BACK"
export BASE_PYTHONPATH=$HOME/localpy/Python-2.7.11/python #bare bones python2.7.. needed to set up virtualenv 
export CA= #Needed for https
export CERT= #Needed for https
export DATA_ROOT=/home/duncan/data
export DEBUG=1
export FLASK_DEBUG=1
export HEXMAP=
export HUB_DBPATH=/home/duncan/hex/compute/db/map.db
export HUB_PATH=/home/duncan/hex/compute
export KEY= #Needed for https
export PYENV=/home/duncan/hex/env
export TEST_DATA_ROOT=/home/duncan/hex/compute/tests/in/dataRoot
export TETE_PATH=$HOME/pypackages/tete
export USE_HTTPS=0 #Set to one if HTTPS desired. Otherwise server boots to HTTP
export VIEWER_URL=http://localhost:3333
export WWW_PATH=$HUB_PATH/www
export WWW_SOCKET=127.0.0.1:5000

export PYTHONPATH=$TETE_PATH:$PTYHONPATH

# If the python environment is present then open it up.
if [ -e $PYENV/bin/activate ]; then
    source $PYENV/bin/activate
fi
