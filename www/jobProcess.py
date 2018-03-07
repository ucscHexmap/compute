#!/usr/bin/env python2.7

# The independent process under which a job runs, internal implementation of
# the API in job.py

import sys
import os, traceback, datetime, json, importlib
try:
    from thread import get_ident
except ImportError:
    from dummy_thread import get_ident

from util_web import AppCtx, Context
from jobQueue import JobQueue

class JobProcess(object):

    def _today (s):
    
        # Today formatted as yyyy-mm-dd.
        return datetime.date.today()

    def _execCalcMain (s, moduleName, parms, ctx):
    
        # Run the job's calcMain().
        if moduleName == None:
            raise ValueError, 'Bad operation module of: ' + operation
        
        # Run the mainCalc function of the given module.
        module = importlib.import_module(moduleName, package=None)
        status, result = module.calcMain(parms, ctx)

        return (status, result)

    def unpackTask (s, packedTask):

        # Unpack the task info into its components.
        unpacked = json.loads(packedTask)

        # Convert the job and app contexts to an instances of the AppCtx class.
        appCtx = AppCtx(unpacked['ctx']['app'])
        del unpacked['ctx']['app']
        ctxDict = {"app": appCtx}
        ctxDict.update(unpacked['ctx'])
        ctx = Context(ctxDict)

        return unpacked['operation'], unpacked['parms'], ctx

    def run (s, id, operation, parms, ctx, moduleName=None):
    
        # Run the job now.
        if moduleName == None:
            moduleName = operation + '_web'

        # Set the status to running.
        s.queue.setStatusRunning(id, os.getpid())

        # Execute the calc main function.
        return s._execCalcMain(moduleName, parms, ctx)

    def __init__(s, queuePath):
        s.queuePath = queuePath
        s._connection_cache = {}
        s.queue = JobQueue(queuePath)

def _formatError (errorMsg, stackTrace, operation, parms):
    result = { 'error': 'server error' }
    if errorMsg:
        result['error'] = errorMsg
    result['stackTrace'] = stackTrace
    if 'map' in parms:
        result['map'] = parms['map']
    return result

def main(args):
    queuePath = args[0]
    id = int(args[1])

    # TODO these should be wrapped with a try-except because any errors here
    # will not be reported in the server log.
    jobProcess = JobProcess(queuePath)
    operation, parms, ctx = jobProcess.unpackTask(jobProcess.queue.getTask(id))

    try:
        status, result = jobProcess.run(id, operation, parms, ctx)
    except Exception as e:
        status = 'Error'
        result = _formatError(str(e), traceback.format_exc(), operation, parms)
    except:
        status = 'Error'
        result = _formatError(None, traceback.format_exc(), operation, parms)

    # Set the completion status.
    JobQueue(queuePath).setResult(id, status, result, ctx, operation)

if __name__ == "__main__" :
    try:
        return_code = main(sys.argv[1:])
    except:
        traceback.print_exc()
        return_code = 1

    sys.exit(return_code)
