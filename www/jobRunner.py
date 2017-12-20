
# The job runner.

import os, traceback, datetime, json, importlib
from multiprocessing import Process
try:
    from thread import get_ident
except ImportError:
    from dummy_thread import get_ident

from util_web import Context, ErrorResp
from jobQueue import JobQueue
import jobQueue

class JobRunner(object):

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

    def _runner (s, id, task, moduleName=None):

        # Run a job in this new process just created given a packed task.
        
        # Get this process ID.
        processId = os.getpid()
        
        # Attach this process to the jobQueue.
        s.queue = JobQueue(s.jobQueuePath)

        # Set the job's status to 'running' and save it's process ID.
        #with s._getConn() as conn:
        #    conn.execute(s.queue._dbSetRunning, (processId, s._today(), id,))
        
        # Pull the components out of the jobQueue task.
        ctx, operation, parms = s._unpackTask(task)
        
        if moduleName == None:
            moduleName = s._findModuleName(operation)
        
        # Execute the calc main function.
        status, result = s._execCalcMain(moduleName, parms, ctx)
        
        # Update the status and result in the jobQueue.
        #print "_runner():id:", id
        #print "_runner():status:", status
        #print "_runner():result:", result

        s._setDoneStatus(id, status, result)

    def _getNextToRun(s):
        with s._getConn() as conn:
            rows = conn.execute(s.queue._dbNextToRun)
            for row in rows:
                return row

    def _runNext (s):
    
        # Look for a job ready to run.
        # If found, start up a new process to run the job.
        job = s._getNextToRun()
        if job == None:
            return # No jobs to run

        id = job[s.queue.idI]

        # Set the job's status to 'running'.
        with s._getConn() as conn:
            conn.execute(s.queue._dbSetRunning, (s._today(), id,))

        # TODO we shouldn't need this:
        # Required to force db update before executing the job.
        r = jobQueue.getStatus(id, s.jobQueuePath)

        # Create a new independent process and run the job.
        p = Process(target=s._runner, args=(id, job[s.queue.taskI],))
        p.start()
        p.join()
    
    def _pollForNew (s, conn):
    
        # Poll for new jobs.
        # TODO: periodically call _runNext() to check for new jobs.
        # For now we execute jobs as they are added, so no need to poll yet.
        pass

    def __init__(s, jobQueuePath):
    
        # Connect to the queue database, creating if need be.
        s.jobQueuePath = os.path.abspath(jobQueuePath)
        s._connection_cache = {}
        s.queue = JobQueue(jobQueuePath)

    def _add (s, user, operation, parms, ctx):
    
        #print '_add():ctx.app:', str(ctx.app)
    
        # Add a job to the end of the job queue.
        # An empty dict is used as the result value
        # so it may be jsonized and de-jsonized without complaints.
        with s._getConn() as conn:
            curs = conn.cursor()
            curs.execute(s.queue._dbPush,
                (s.queue.inJobQueueSt, user, s._today(), s._packTask(operation, parms, ctx),))
            jobId = curs.lastrowid
            
            # Save the id and status.
            r = jobQueue.getStatus(jobId, s.jobQueuePath)
            
            #print '_add():ctx.app.unitTest:', str(ctx.app.unitTest)

            if not ctx.app.unitTest:

                # Get the next job immediately so we don't wait for the polling.
                s._runNext()
            
            # Return the id and status.
            return (jobId, r['status'])
            
# Public interface #########################################################

def add (user, operation, parms, ctx):

    # Add a job to the tail end of the job queue.
    # @param         user: username requesting the job
    # @param    operation: job operation to run; the python module that
    #                      contains the calcMain() function should be in the
    #                      file, <operation>_www.py
    # @param        parms: parameters as a python dict to be passed to
    #                      <operation>_www.py.calcMain()
    # @params         ctx: the context holding information for the postCalc
    # @returns: (jobId, status)
    r = JobRunner(ctx.app.jobQueuePath)._add(user, operation, parms, ctx)
    return { 'jobId': r[0], 'status': r[1] }
    #return jobRunner.add(None, 'jobTestHelper', data, ctx)

# calcMain()
# Each operation needs a function defined in <operation>_www.py as below
# for the job runner to execute the operation and save the result in the job
# queue.

# calcMain (parms, ctx)
# The entry point to the calc operation which may transform the parameters
# into a convenient form for the calc routine that actually does the work.
# @param parms: parameters to the calc routine as a python dict
# @param   ctx: information needed for the calc post processing
# returns: (status, result) where status is 'Success' or 'Error;
#          result is optional returned data on success and on error, the
#          error message and optional stack trace


