#!/usr/bin/env python2.7

# A helper for job tests as well as an example of an operation, 'jobTestHelper',
# making use of the job API.

import time
import job

secondsToRun = 0.3

def _validateParms (data):

    # Whatever validation that may be done to return immediate feedback
    # to the caller.
    # Use ErrorResp here to report errors.
    return

def preCalc(data, ctx):
    
    # The entry point from URL routing to prepare the data for saving in the
    # job queue.
    # Use ErrorResp here to report errors.
    # @param data: the data from the HTTP post request
    # @param ctx: the job context
    # @returns: the result of the call to job.add(), an object like:
    #           { 'jobId': <jobId>, 'status': <status> }
    
    _validateParms(data)
    
    if data['testStatus'] == 'InJobQueue':
    
        # Set unitTest to True so the job will not be run immediately and we
        # have a chance to see the status of 'InJobQueue' before is it changed
        # to 'Running'.
        ctx.app.unitTest = True
    else:
    
        # Set unitTest to False so the job will run immediately.
        ctx.app.unitTest = False

    # Add this task to the job queue.
    return job.add(None, 'jobTestHelper', data, ctx)

def _postCalc ():

    # Whatever post calculation work to be done before storing the result in
    # the job database.
    # Use standard exceptions here to report errors.
    return

def calcMain (parms, ctx):

    # The main process in which the job executes.
    # Use standard exceptions here to report errors.
    # @param parms: the parameters for the operation
    # @param ctx: the job context
    # @returns: (status, result) where the status is 'Success' or 'Error'
    #           and the result depends on the status:
    #               Success: None or a dict containing anything
    #               Error: None or a dict containing one of the below:
    #                       {'error': <message>}
    #                       {'error': <message>, 'stackTrace': <trace>}
    
    result = {'myResult': 'result1'}

    if 'testStatus' in parms:
        if parms['testStatus'] == 'Running':
            time.sleep(secondsToRun)
            _postCalc()
            return ('Success', result)
        elif parms['testStatus'] == 'Success':
            _postCalc()
            return ('Success', None)
        elif parms['testStatus'] == 'SuccessResult':
            _postCalc()
            return ('Success', result)
        elif parms['testStatus'] == 'Error':
            return ('Error', None)
        elif parms['testStatus'] == 'ErrorResult':
            return ('Error', {"error": "some error"})
        elif parms['testStatus'] == 'ErrorTrace':
            return ('Error', {"error": "some error", "stackTrace": "some stackTrace"})

    return ('Success', result)
