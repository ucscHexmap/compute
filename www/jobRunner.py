
# The job runner.

import os, sqlite3, traceback, datetime, json, importlib
#from threading import Thread
try:
    from thread import get_ident
except ImportError:
    from dummy_thread import get_ident

from jobQueue import JobQueue
import jobQueue

class JobRunner(object):

    # Sqlite database access.
    _dbSetRunning = (
        'UPDATE queue '
        'SET status = "' + JobQueue.runningSt + '", processId = ?, lastAccess = ? '
        'WHERE id = ?'
    )
    _dbNextToRun = (
        'SELECT * FROM queue '
        'WHERE status = "' + JobQueue.inJobQueueSt + '" LIMIT 1'
    )
    _dbSetResult = (
        'UPDATE queue '
        'SET status = ?, result = ?, lastAccess = ? '
        'WHERE id = ?'
    )

    def _getConn (s):
    
        # Get the sqlite connection for this thread where isolation_level=None
        # tells sqlite to commit automatically after each db update.
        id = get_ident()
        if id not in s._connection_cache:
            s._connection_cache[id] = \
                sqlite3.connect(s.jobQueuePath, timeout=60, isolation_level=None)

        return s._connection_cache[id]

    def _setResult (s, id, status, result=None):
    
        # Set the status and optional result.
        with s._getConn() as conn:
            conn.execute(s._dbSetResult, (status, result, s.jq.today(), id,))

        # Email to user if there is a result?
        # if result != None:
        #   TODO email user

    def _findModuleName (s, operation):
    
        # Find the name of the module that contains the calcMain() for this
        # operation.
        moduleName = None
        try:
            moduleName = operation + '_www'
        except:
            pass
        return moduleName
    
    def _execCalcMain (s, moduleName, parms):
    
        # Run the job's calcMain().
        if moduleName == None:
            raise ValueError, 'Bad job operation of: ' + operation
        
        # Run the mainCalc function of the given module.
        module = importlib.import_module(moduleName, package=None)
        status, result = module.calcMain(parms)
        return (status, result)

    def _unpackTask (s, packedTask):
    
        # Unpack the task info into its components.
        unpacked = json.loads(packedTask)
        return unpacked['operation'], unpacked['parms'], unpacked['ctx']

    def _runner (s, id, task, moduleName=None):

        # Run a job in this new process just created.
        
        # Get this process ID.
        processId = os.getpid()
        
        # Attach this process to the jobQueue.
        s.jq = JobQueue(s.jobQueuePath)

        # Set the job's status to 'running' and save it's process ID.
        with s._getConn() as conn:
            conn.execute(s._dbSetRunning, (processId, s.jq.today(), id,))
        
        # Pull the components out of the jobQueue task.
        operation, parms, ctx = s._unpackTask(task)
        
        if not moduleName:
            moduleName = s._findModuleName (operation)
        
        # Execute the calc main function.
        status, result = s._execCalcMain(moduleName, parms)
        
        # Update the status and result in the jobQueue.
        s._setResult(id, status, result)

    def _getNextToRun(s):
        with s._getConn() as conn:
            rows = conn.execute(s._dbNextToRun)
            for row in rows:
                return row

    def _runNext (s):
    
        # Look for a job ready to run.
        # If found, start up a new process to run the job.
        job = s._getNextToRun()
        if job == None:
            return # No jobs to run
        
        '''
        # Create a new thread and run the job.
        thread = Thread(target = s._runner,
            args = (job[s.idI], job[s.taskI]))
        thread.start()
        #thread.join()
        #print "thread finished...exiting"
        '''
        
        # Create a new independent process and run the job.
        parentPid=os.fork()
        if not parentPid:
            s._runner (job[s.jq.idI], job[s.jq.taskI])

    def _pollForNew (s, conn):
    
        # Poll for new jobs.
        # TODO: periodically call _runNext() to check for new jobs.
        # For now we execute jobs as they are added, so no need to poll yet.
        pass

    def __init__(s, jobQueuePath):
    
        # Connect to the queue database, creating if need be.
        s.jobQueuePath = os.path.abspath(jobQueuePath)
        s._connection_cache = {}
        s.jq = JobQueue(jobQueuePath)

    # Public interface #########################################################

    # Each operation needs a function defined in <operation>_www.py as below
    # for the job runner to execute the operation and save the result in the job
    # queue.

    # calcMain (parms, ctx)
    # The entry point to the calc operation which may transform the parameters
    # into a convenient form before calling the calc routine that does the work.
    # @param parms: parameters to the calc routine as a python dict
    # @param   ctx: information needed for the calc post processing
    # returns: (status, result) where status is 'Success' or 'Error;
    #          result is optional returned data on success and on error, the
    #          error message and optional stack trace


