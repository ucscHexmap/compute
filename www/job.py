
# job.py
# Handles job control of calc processes

import os, json, types, requests, traceback, csv, logging, datetime
import util_web
from util_web import SuccessResp, ErrorResp, getMapMetaData

jobs = {};
jobSeq = 1;

def _removeOldJobIds ():
    '''
    TODO
    Remove old jobs mostly so we don't fill up memory with job info that no one
    cares about anymore. Someday this should be stored offline.
    '''
    pass

def _setStatus (id, status):
    jobs[id]['status'] = status
    jobs[id]['lastUpdateTime'] = str(datetime.datetime.now())[5:-7]

def processComplete (id, result):
    '''
    Save the status and result upon process completion.
    @param id: the job ID
    @param result: the result of the computation
    @return: calls the callback if there is one
    '''
    # TODO use proc.communicate so we are notified when the process is complete
    try:
        j = jobs[id]
    except:
        raise Exception('No such job with ID: ' + id)

    # The job has completed without errors
    if 'callback' in j:
        j['callback'](result, j['ctx'])

def getStatus (id):
    '''
    Return the job status, which is one of:
        Request received
        Success
        Error
    @param id: the job ID
    @return: {
        'status': <status>,
        'result': <result>,
    }
    '''
    try:
        j = jobs[id]
    except:
        raise Exception('No such job with ID: ' + id)
    return {
        'status': j['status'],
        'result': j['result'],
    }
    # OR: return (j['status'], j['result'])

def new (process, callback, ctx):
    '''
    Add a new process to the jobs dict
    @param  process: an instance of Popen.
    @param callback: the function to be called when the job completes as:
                     callback(result, ctx)
    @param      ctx: the context to be included in the callback
    @return: the job ID
    '''
    id = str(jobSeq)
    jobSeq += 1
    jobs[id] = {
        'process': process,
        'result': None,
        'callback': callback,
        'ctx': ctx,
    }
    _setStatus(id, status)
    process.communicate(stdout=PIPE, stderr=PIPE)

    return id

