
import os
import time
import forkIt

app = {
    'prop': 'a property of app'
}
aSharedVar = 7

pid = os.fork()
if pid:
    # immediate response to http client
    while True:
        print "I'm the parent with shared:", aSharedVar
        time.sleep(0.5)
else:
    # a process to hang around until the calc routine completes.
    while True:
        aSharedVar += 1
        print "I'm just a child with shared:", aSharedVar
        time.sleep(0.5)
        
