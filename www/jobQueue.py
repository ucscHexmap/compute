
'''
jobQueue.py
A job queue using sqlite.
Thanks to Thiago Arruda from http://flask.pocoo.org/snippets/88/
Can be used in the same way as with redit: http://flask.pocoo.org/snippets/73/
'''

import os, sqlite3
from cPickle import loads, dumps
from time import sleep
try:
    from thread import get_ident
except ImportError:
    from dummy_thread import get_ident

inJobQueue = 'in job queue'

WAITING_TO_RUN = 'waiting to run'
RUNNING = 'running'
SUCCESS ='success'
ERROR = 'error'

class JobQueue(object):

    # sql commands
    _create = (
        'CREATE TABLE IF NOT EXISTS queue '
        '('
        '  id INTEGER PRIMARY KEY AUTOINCREMENT,'
        '  status text,'
        '  task text'
        ')'
    )
    _push = 'INSERT INTO queue (status, task) VALUES (?, ?)'
    _getOneById = (
        'SELECT id, status, task FROM queue '
        'WHERE id = ?'
    )
    _getAll = (
        'SELECT id, status, task FROM queue '
        'ORDER BY id'
    )
    _setStatus = (
        'UPDATE queue '
        'SET status = ? '
        'WHERE id = ?'
    )
    _getNextToRun = (
        'SELECT id, status, task FROM queue '
        'WHERE status = "' + WAITING_TO_RUN + '" LIMIT 1'
    )

    _count = 'SELECT COUNT(*) FROM queue'
    _iterate = 'SELECT id, status, task FROM queue'
    #_lastInsertedRowId = 'SELECT last_insert_rowid()'
    #_lastInsertedRowId = 'SELECT LAST_INSERT_ROWID'
    _lastInsertedRowId = 'SELECT MAX(id)'
    _write_lock = 'BEGIN IMMEDIATE'
    _popleft_get = (
            'SELECT id, status, task FROM queue '
            'ORDER BY id LIMIT 1'
            )
    _popleft_del = 'DELETE FROM queue WHERE id = ?'

    def __init__(s, path):
        s.path = os.path.abspath(path)
        s._connection_cache = {}
        with s._get_conn() as conn:
            conn.execute(s._create)
        
        # Status values
        s.requestReceived = 'request received'
        s.success ='success'
        s.error = 'error'
        
        # Column indices when all columns are included in the row.
        s.idI = 0
        s.statusI = 1
        s.taskI = 2

    def __len__(self):
        with self._get_conn() as conn:
            l = conn.execute(self._count).next()[0]
        return l

    def __iter__(self):
        with self._get_conn() as conn:
            for id, obj_buffer in conn.execute(self._iterate):
                yield loads(str(obj_buffer))

    def _get_conn(self):
    
        # Get the sqlite connection for this thread.
        id = get_ident()
        if id not in self._connection_cache:
            self._connection_cache[id] = sqlite3.Connection(self.path,
                    timeout=60)
        return self._connection_cache[id]

    def popleft(self, sleep_wait=True):
        keep_polling = True
        wait = 0.1
        max_wait = 2
        tries = 0
        with self._get_conn() as conn:
            id = None
            while keep_polling:
                conn.execute(self._write_lock)
                cursor = conn.execute(self._popleft_get)
                try:
                    id, obj_buffer = cursor.next()
                    keep_polling = False
                except StopIteration:
                    conn.commit() # unlock the database
                    if not sleep_wait:
                        keep_polling = False
                        continue
                    tries += 1
                    sleep(wait)
                    wait = min(max_wait, tries/10 + wait)
            if id:
                conn.execute(self._popleft_del, (id,))
                return loads(str(obj_buffer))
        return None
    
    def setStatus (s, id, status):
        with s._get_conn() as conn:
            conn.execute(s._setStatus, (status, id,))

    def getNextToRun (s):
         with s._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            curs = conn.cursor()
            curs.execute(s._getNextToRun)
            row = curs.fetchone()
            conn.execute(s._setStatus, (status, id,))
    
    def getStatus (s, id):
        with s._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            curs = conn.cursor()
            curs.execute(s._getOneById, (id,))
            row = curs.fetchone()
            return row[s.statusI]

    def getAll(s, file=None):
        with s._get_conn() as conn:
            all = conn.execute(s._getAll)
            if file:
                with open('dump.sql', 'w') as f:
                    for line in dump:
                        f.write('%s\n' % line)
            else:
                return conn.execute(s._getAll)
    
    def push(s, task):
        with s._get_conn() as conn:
            curs = conn.cursor()
            curs.execute(s._push, (WAITING_TO_RUN, task,))
            conn.commit()
            
            # Return the id.
            return curs.lastrowid


