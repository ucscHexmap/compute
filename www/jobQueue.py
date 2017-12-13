
# The job queue.

import os, sqlite3, traceback, datetime, json
from peewee import *

try:
    from thread import get_ident
except ImportError:
    from dummy_thread import get_ident

class JobQueue(object):

    # Job statuses.
    inJobQueueSt = 'InJobQueue'
    runningSt = 'Running'
    successSt ='Success'
    errorSt = 'Error'
    # future: cancelSt = 'Cancelled'
    
    # Column indices.
    idI = 0
    statusI = 1
    userI = 2
    lastAccessI = 3
    processIdI = 4
    taskI = 5
    resultI = 6
    
    # Errors returned from public functions.
    errorInvalidArgs = 'errorInvalidArgs'
    errorBadStateChangeFrom = 'errorBadStateChangeFrom'
    
    # Sqlite database access.
    _dbCreate = (
        'CREATE TABLE IF NOT EXISTS queue '
        '('
        '  id INTEGER PRIMARY KEY AUTOINCREMENT,'
        '  status text,'
        '  user text,'
        '  lastAccess text,'
        '  processId integer,'
        '  task text,'
        '  result text'
        ')'
    )
    _dbPush = (
        'INSERT INTO queue (status, user, lastAccess, task, result) '
        'VALUES (?, ?, ?, ?, ?)'
    )
    _dbGetById = (
        'SELECT * FROM queue '
        'WHERE id = ?'
    )
    _dbGetAll = (
        'SELECT * FROM queue '
        'ORDER BY id'
    )
    _dbRemoveById = (
        'DELETE FROM queue '
        'WHERE id = ?'
    )
    _dbSetRunning = (
        'UPDATE queue '
        'SET status = "' + runningSt + '", processId = ?, lastAccess = ? '
        'WHERE id = ?'
    )
    _dbNextToRun = (
        'SELECT * FROM queue '
        'WHERE status = "' + inJobQueueSt + '" LIMIT 1'
    )
    _dbSetResult = (
        'UPDATE queue '
        'SET status = ?, result = ?, lastAccess = ? '
        'WHERE id = ?'
    )

    def getConnection (s):
        return sqlite3.connect(s.path, timeout=60, isolation_level=None)
    
    def _getConn (s):
    
        # Get the sqlite connection for this thread where isolation_level=None
        # tells sqlite to commit automatically after each db update.
        id = get_ident()
        if id not in s._connection_cache:
            s._connection_cache[id] = s.getConnection()

        return s._connection_cache[id]

    def _cullOld (s, conn):
    
        # TODO Clean up by removing any jobs older than a certain age.
        # Older than a month?
        # Once per day?
        pass
    
    def __init__(s, path):
    
        # Connect to the queue database, creating if need be.
        s.path = os.path.abspath(path)
        s._connection_cache = {}
        with s._getConn() as conn:
            conn.execute(s._dbCreate)

    def _getAll (s, file=None):
        
        # Get every row in the job queue, writing to a file, or to memory.
        # Probably only for debugging and testing.
        with s._getConn() as conn:
            all = conn.execute(s._dbGetAll)
            if file:
                with open('dump.sql', 'w') as f:
                    for row in all:
                        f.write('%s\n' % line)
            else:
                rows = []
                for row in all:
                    rows.append(row)
                return rows
    
    def _getOne (s, id):

        # Get the entire row for the given ID.
         with s._getConn() as conn:
            get = conn.execute(s._dbGetById, (id,))
            job = None
            for row in get:
                job = row
            return job

    def _getStatus (s, id):
    
        # Get the status of one job.
        row = s._getOne(id)
        if row == None:
            return None
        else:
            return { 'status': row[s.statusI], 'result': row[s.resultI] }

    # Future public functions ##################################################

    def remove (s, id):
    
        # Remove a job from the queue.
        # TODO we should not allow removal of running jobs. They should be
        # cancelled first.
        with s._getConn() as conn:
            conn.execute(s._dbRemoveById, (id,))

    def cancel (s, id):
    
        # Mark a job as cancelled and save the error message.
        pass # TODO

    def getByUser (s, user):

        # Get all jobs owned by the given user.
        pass # TODO

# Public functions #########################################################

def getStatus (id, appCtx):

    # Retrieve the status and result of the given job ID.
    # @param id: the job ID
    # @param appCtx: the app context
    # @returns: status and result as a dict of the job or None if job not
    #           found; only Success and Error have a result, others return an
    #           empty dict ({}) for the result so there are no json
    #           conversion complaints.
    return JobQueue(appCtx.jobQueuePath)._getStatus(id)

