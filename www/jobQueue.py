
# The job queue.

import os, sqlite3, traceback, datetime, json
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

    def _getConn (s):
    
        # Get the sqlite connection for this thread where isolation_level=None
        # tells sqlite to commit automatically after each db update.
        id = get_ident()
        if id not in s._connection_cache:
            s._connection_cache[id] = \
                sqlite3.connect(s.path, timeout=60, isolation_level=None)

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
    
    def _packTask (s, operation, parms, ctx):
    
        # Pack the task info into a json string.
        task = {
            'operation': operation,
            'parms': parms,
            'ctx': ctx,
        }
        return json.dumps(task, separators=(',',':'), sort_keys=True)

    def _getOne (s, id):

        # Get the entire row for the given ID.
         with s._getConn() as conn:
            get = conn.execute(s._dbGetById, (id,))
            job = None
            for row in get:
                job = row
            return job

    def today (s):
    
        # Today formatted as yyyy-mm-dd.
        return datetime.date.today()

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

    def getStatus (s, id):
    
        # Retrieve the status and result of the given job ID.
        # @param id: the job ID
        # @returns: (status, result) of the job or None if job not found;
        #           only Success and Error have a result, others return None
        row = s._getOne(id)
        if row == None:
            return None
        else:
            return (row[s.statusI], row[s.resultI])

    def add (s, user, operation, parms, ctx, waitForPoll=False):
    
        # Add a job to the tail end of the job queue.
        # @param         user: username requesting the job
        # @param    operation: job operation to run
        # @param        parms: the parameters to be passed to calcMain()
        # @params         ctx: the context holding information for the postCalc
        # @params waitForPoll: True to wait for the polling to look for new jobs
        #                      False to look for new jobs immediately
        # @returns: the job ID
        with s._getConn() as conn:
            curs = conn.cursor()
            curs.execute(s._dbPush,
                (s.inJobQueueSt, user, s.today(),
                s._packTask(operation, parms, ctx),))
            jobId = curs.lastrowid

            if not waitForPoll:

                # Get the next job immediately so we don't wait for the polling.
                s._getNextJob()
            
            # Return the id and status, but not result.
            status, result = s.getStatus(jobId)
            return (jobId, status)
