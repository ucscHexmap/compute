
export ADMIN_EMAIL=dmccoll@ucsc.edu
export BACK_OR_FOREGROUND=FORE #"FORE" or "BACK"
export CA= #Needed for https
export CERT= #Needed for https
export DATA_ROOT=/home/duncan/data
export DEBUG=1
export DEV=1
export FLASK_DEBUG=1
export HEX_UID=dmccoll
export HUB_DBPATH=/home/duncan/hex/compute/db/map.db
export KEY= #Needed for https
export PORT=5000
export PYENV=/home/duncan/hex/env
export DEPLOY_TARGET_PATH=plaza.gi.ucsc.edu:
export TEST_DATA_ROOT=/home/duncan/hex/compute/tests/in/dataRoot
export TETE_PATH=$HOME/pypackages/tete
export USE_HTTPS=0 #Set to one if HTTPS desired. Otherwise server boots to HTTP
export VIEWER_URL=http://localhost:3333
export WWW_SOCKET=127.0.0.1:$PORT
export DATA_HOST_PORT=$WWW_SOCKET

# If the python environment is present then open it up.
if [ -e $PYENV/bin/activate ]; then
    source $PYENV/bin/activate
fi
