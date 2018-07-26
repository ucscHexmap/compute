
Scripts in this directory:

Server operations:
    cd $HEXCALC
    bin/start
    bin/stop
    bin/restart

Or for server operations for protected ports:
    sudo $HEXCALC/bin/start
    sudo $HEXCALC/bin/stop

deployWww: make a tar file to update another installation

installWww: extract from a tar file on the target installation

lint.sh: runs lint

runTest: run the unit tests

showJobs: show any python processes belonging to the server username

showProc: show any server processes running
