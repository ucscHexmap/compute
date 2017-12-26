
# The job queue.

import os, sqlite3, traceback, datetime, json
try:
    from thread import get_ident
except ImportError:
    from dummy_thread import get_ident

from util_web import ErrorResp

class JobQueue(object):

    # Job statuses.
    inJobQueueSt = 'InJobQueue'
    runningSt = 'Running'
    successSt ='Success'
    errorSt = 'Error'
    
    # Column indices.
    idI = 0
    statusI = 1
    userI = 2
    lastAccessI = 3
    processIdI = 4
    taskI = 5
    resultI = 6
    
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
        'INSERT INTO queue (status, user, lastAccess, task) '
        'VALUES (?, ?, ?, ?)'
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
        'SET status = "' + runningSt + '", lastAccess = ?, processId = ? '
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
    
        # Get the sqlite connection for this thread where isolation_level=None
        # tells sqlite to commit automatically after each db update.
        return sqlite3.connect(s.queuePath, timeout=60, isolation_level=None)
    
    def _getConn (s):
    
        # Get the sqlite connection for this thread..
        id = get_ident()
        if id not in s._connection_cache:
            s._connection_cache[id] = s.getConnection()

        return s._connection_cache[id]

    def _today (s):
    
        # Today formatted as yyyy-mm-dd.
        return datetime.date.today()

    def __init__(s, queuePath):
    
        # Connect to the queue database, creating if need be.
        s.queuePath = queuePath
        s._connection_cache = {}
        with s._getConn() as conn:
            conn.execute(s._dbCreate)

    def _getOne (s, id):

        # Get the entire row for the given ID.
         with s._getConn() as conn:
            get = conn.execute(s._dbGetById, (id,))
            job = None
            for row in get:
                job = row
            return job

    def getAll (s, file=None):
        
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

    def getStatus (s, id):
    
        # Get the status of one job.
        row = s._getOne(id)
        if row == None:
            return None
        elif row[s.resultI]:
            return {
                'status': row[s.statusI], 'result': json.loads(row[s.resultI])
            }
        else:
            return { 'status': row[s.statusI] }

    def setResult (s, id, status, jsonResult):
        with s._getConn() as conn:
            conn.execute(s._dbSetResult, (status, jsonResult, s._today(), id,))
    
    def getTask (s, id):
        job = s._getOne(id)
        if job == None:
            return None
        return job[s.taskI]

    def setStatusRunning (s, id, processId=None):
    
        # Set the job's status to 'running'.
        with s.getConnection() as conn:
            conn.execute(s._dbSetRunning, (s._today(), processId, id,))

    def add (s, id, packedTask, user):
    
        # Add a job to the job queue.
        with s._getConn() as conn:
            curs = conn.cursor()
            curs.execute(s._dbPush, (s.inJobQueueSt, user, s._today(), packedTask,))
            return curs.lastrowid
