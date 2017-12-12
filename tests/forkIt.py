
import os
import time

app = {
    'prop': 'a property of global app'
}
aSharedVar = 7

pid=os.fork()
if pid:
    # parent
    while True:
        print "I'm the parent with shared:", aSharedVar
        time.sleep(0.5)
else:
    # child
    while True:
        aSharedVar += 1
        print "I'm just a child with shared:", aSharedVar
        time.sleep(0.5)
        
