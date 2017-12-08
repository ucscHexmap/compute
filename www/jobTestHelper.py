#!/usr/bin/env python2.7

# A helper for job tests

import time
def calcMain (parms):

    # Give the job runner a chance to set the status to Running.
    time.sleep(0.01)
    return ('Success', 'result1')
