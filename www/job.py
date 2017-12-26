
# The job manager.

import os, traceback, datetime, json, importlib
from multiprocessing import Process
import subprocess
try:
    from thread import get_ident
except ImportError:
    from dummy_thread import get_ident

from util_web import Context, ErrorResp
from jobQueue import JobQueue

def _packTask (operation, parms, ctx):

    # Pack the task info into a json string.
    task = {
        'operation': operation,
        'parms': parms,
        'ctx': ctx,
    }
    jsonTask = json.dumps(task, default=lambda o: o.__dict__,
        separators=(',',':'), sort_keys=True)
        
    return jsonTask
    
def _runNow(id, queuePath):

    # Run the operation in a new process.
    p = subprocess.Popen(['jobProcess.py', queuePath, str(id)])

def getAll (queuePath):

    # Dump all jobs in the queue.
    # @param queuePath: the job queue path
    # @returns: an array of jobs in an object
    return { 'jobs': JobQueue(queuePath).getAll() }

def getStatus (id, queuePath):

    # Retrieve the status and result of the given job ID.
    # @param id: the job ID
    # @param queuePath: the job queue path
    # @returns: a dict of the form: {'status': <status>, 'result': <dict>}
    #           where result is None if the job is not found;
    #           only Success and Error may have an optional result; if
    #           there is no result, no result property is returned
    statusResult = JobQueue(queuePath).getStatus(id)
    if statusResult == None:
        raise ErrorResp('unknown job ID of: ' + str(id))
    return statusResult

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
    
    # Add a job to the job queue.
    queuePath = ctx.app.jobQueuePath
    jobId = JobQueue(queuePath).add(id, _packTask(operation, parms, ctx), user)
    
    # Get the status of the job just added to the queue.
    r = getStatus(jobId, queuePath)

    print "add():ctx.app.unitTest:", ctx.app.unitTest

    # Run the job now.
    if not ctx.app.unitTest:
        _runNow(jobId, queuePath)

    # Return the id and status.
    return { 'jobId': jobId, 'status': r['status'] }

# calcMain()
# Each operation needs a function defined in <operation>_www.py as below
# for the job runner to execute the operation and save the result in the job
# queue.
#
# calcMain (parms, ctx)
# The entry point to the calc operation which may transform the parameters
# into a convenient form for the calc routine that actually does the work.
# @param parms: parameters to the calc routine as a python dict
# @param   ctx: information needed for the calc post processing
# returns: (status, result) where status is 'Success' or 'Error;
#          result is optional returned data on success and on error, the
#          error message and optional stack trace
