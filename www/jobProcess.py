#!/usr/bin/env python2.7

# The independent process under which a job runs.
import sys
import os, traceback, datetime, json, importlib
try:
    from thread import get_ident
except ImportError:
    from dummy_thread import get_ident

from util_web import Context
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

    def _unpackTask (s, packedTask):

        # Unpack the task info into its components.
        unpacked = json.loads(packedTask)

        # Convert the job and app contexts to an instances of the Context class.
        ctx = Context(unpacked['ctx'])
        appCtx = Context(ctx.app)

        # Replace ctx.app as a dict with the appCtx Context class instance.
        ctx.app = appCtx

        return ctx, unpacked['operation'], unpacked['parms'],

    def run (s, id, moduleName=None):

        # Run the job now.
        ctx, operation, parms = s._unpackTask(s.queue.getTask(id))
        
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

def _setDoneStatus (queuePath, id, status, result=None):

    # Set the status and optional result.
    if result != None:
        jsonResult = json.dumps(result, sort_keys=True)
    else:
        jsonResult = None
    
    JobQueue(queuePath).setResult(id, status, jsonResult)

    # TODO Email to user?

def main(args):
    queuePath = args[0]
    jobId = int(args[1])
    try:
        jobProcess = JobProcess(queuePath)
        status, result = jobProcess.run(jobId)
    except Exception as e:
        status = 'Error'
        result = { 'error': repr(e), 'stackTrace': traceback.format_exc() }
    
    # Set the completion status.
    _setDoneStatus(queuePath, jobId, status, result)

if __name__ == "__main__" :
    try:
        return_code = main(sys.argv[1:])
    except:
        traceback.print_exc()
        return_code = 1

    sys.exit(return_code)
