#!/usr/bin/env python2.7

# A helper for job tests

import time
import jobRunner

def preCalc(data, ctx):
    
    # The entry point from the www URL routing.
    # @param data: the data from the HTTP post request
    # @param ctx: the job context
    # @returns: nothing
    
    # So the job is run immediately.
    ctx.app.unitTest = False
    #print 'preCalc():data:', data
    if data['testStatus'] == 'InJobQueue':
        #print "preCalc():data['testStatus'] == 'InJobQueue'"
        ctx.app.unitTest = True
    elif data['testStatus'] == 'Running':
        data['timeout'] = 2
    return jobRunner.add(None, 'jobTestHelper', data, ctx)

def calcMain (parms, ctx):

    # The main process in which the job executes.
    # @param parms: the parameters for the operation
    # @param ctx: the job context
    # @returns: (status, result) where status is 'Success' or 'Error'
    #           and result is a dict with the following possible values:
    #           success: None or a dict containing anything
    #           error: None or a dict containing one of the below:
    #           {'error': <message>}
    #           {'error': <message>, 'stackTrace': <trace>}
    
    result1 = {'myResult': 'result1'}

    if 'timeout' in parms:

        # Give the job runner a chance to set the status to Running.
        time.sleep(parms['timeout'])
        return ('Success', result1)
    elif 'testStatus' in parms:
        if parms['testStatus'] == 'Success':
            return ('Success', None)
        elif parms['testStatus'] == 'SuccessResult':
            return ('Success', result1)
        elif parms['testStatus'] == 'Error':
            return ('Error', None)
        elif parms['testStatus'] == 'ErrorResult':
            return ('Error', {"error": "some error"})
        elif parms['testStatus'] == 'ErrorTrace':
            return ('Error', {"error": "some error", "stackTrace": "some stackTrace"})

    return ('Success', result1)
