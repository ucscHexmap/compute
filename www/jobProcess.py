#!/usr/bin/env python2.7

# The independent process under which a job runs.
import sys
import os, traceback, datetime, json, importlib
from multiprocessing import Process
import subprocess
try:
    from thread import get_ident
except ImportError:
    from dummy_thread import get_ident

from util_web import Context, ErrorResp
from jobQueue import JobQueue
import jobQueue

class JobProcess(object):

    def _getConn (s):
    
        # Get the sqlite connection for this thread.
        return s.queue.getConnection()

    def _today (s):
    
        # Today formatted as yyyy-mm-dd.
        return datetime.date.today()

    def _setDoneStatus (s, id, status, result=None):

        # Set the status and optional result.
        if result != None:
            jsonResult = json.dumps(result, sort_keys=True)
        else:
            jsonResult = None
        
        with s._getConn() as conn:
            conn.execute(s.queue._dbSetResult,
                (status, jsonResult, s._today(), id,))

        # TODO Email to user?

    def _findModuleName (s, operation):
    
        # Find the name of the module that contains the calcMain() for this
        # operation.
        moduleName = None
        try:
            moduleName = operation + '_web'
        except:
            pass
        return moduleName
    
    def _execCalcMain (s, moduleName, parms, ctx):
    
        # Run the job's calcMain().
        if moduleName == None:
            raise ValueError, 'Bad job operation of: ' + operation
        
        # Run the mainCalc function of the given module.
        module = importlib.import_module(moduleName, package=None)
        
        try:
            status, result = module.calcMain(parms, ctx)
        except Exception as e:
            status = 'Error'
            result = { 'error': repr(e), 'stackTrace': traceback.format_exc() }

        return (status, result)

    def _packTask (s, operation, parms, ctx):
    
        # Pack the task info into a json string.
        task = {
            'operation': operation,
            'parms': parms,
            'ctx': ctx,
        }
        jsonTask = json.dumps(task, default=lambda o: o.__dict__,
            separators=(',',':'), sort_keys=True)
            
        return jsonTask

    def _unpackTask (s, packedTask):
    
        # Unpack the task info into its components.
        unpacked = json.loads(packedTask)

        # Convert the ctx to an instance of the Context class.
        ctx = Context(unpacked['ctx'])
    
        # Convert the app context to an instance of the Context class.
        appCtx = Context(ctx.app)

        # Replace ctx.app as a dict with the appCtx Context class instance.
        ctx.app = appCtx

        return ctx, unpacked['operation'], unpacked['parms'],

    def _getStatus (s, id):
        r = jobQueue.getStatus(id, s.jobQueuePath)
        print 'status is', str(r['status'])

    def _setStatusRunning (s, id, processId=None):
    
        # Set the job's status to 'running'.
        print '_setStatusRunning() before'
        s._getStatus (id)

        with s._getConn() as conn:
            conn.execute(s.queue._dbSetRunning, (s._today(), id,))
            #conn.execute(s.queue._dbSetRunning, (s._today(), '1', id,))
            
            
            
            
            
        print 'set to running'

        # TODO we shouldn't need this:
        # Required to force db update before executing the job.
        s._getStatus(id)

    #def _runner (s, id, task, moduleName=None):
    def _runner (s, id, moduleName=None):
    
        job = s.queue._getOne(id)
        task = job[s.queue.taskI]

        # Run a job in this new process just created given a packed task.
        
        # Get this process ID.
        processId = os.getpid()
        
        # Attach this process to the jobQueue.
        s.queue = JobQueue(s.jobQueuePath)

        #s._setStatusRunning(id, processId)
        
        # Pull the components out of the jobQueue task.
        ctx, operation, parms = s._unpackTask(task)
        
        if moduleName == None:
            moduleName = s._findModuleName(operation)
        
        # Execute the calc main function.
        status, result = s._execCalcMain(moduleName, parms, ctx)
        
        print '_runner(): before setting Done'
        s._getStatus (id)
        
        s._setDoneStatus(id, status, result)
        
        print '_runner(): after setting Done'
        s._getStatus (id)

    def __init__(s, jobQueuePath):
    
        # Connect to the queue database, creating if need be.
        s.jobQueuePath = os.path.abspath(jobQueuePath)
        s._connection_cache = {}
        s.queue = JobQueue(jobQueuePath)

def main(args):
    print 'args:', args
    jobQueuePath = args[0]
    jobId = int(args[1])
    print 'jobQueuePath:', jobQueuePath
    print 'jobId:', jobId
    jobProcess = JobProcess(jobQueuePath)
    jobProcess._runner(jobId)

if __name__ == "__main__" :
    try:
        return_code = main(sys.argv[1:])
    except:
        traceback.print_exc()
        return_code = 1

    sys.exit(return_code)
