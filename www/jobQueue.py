'''
jobQueue.py
Thanks to Thiago Arruda from http://flask.pocoo.org/snippets/88/
Can be used in the same way as http://flask.pocoo.org/snippets/73/
'''
import os, sqlite3
from cPickle import loads, dumps
from time import sleep
try:
    from thread import get_ident
except ImportError:
    from dummy_thread import get_ident


class JobQueue(object):

    _create = (
            'CREATE TABLE IF NOT EXISTS queue ' 
            '('
            '  id INTEGER PRIMARY KEY AUTOINCREMENT,'
            '  item BLOB'
            ')'
            )
    _count = 'SELECT COUNT(*) FROM queue'
    _iterate = 'SELECT id, item FROM queue'
    _append = 'INSERT INTO queue (item) VALUES (?)'
    _write_lock = 'BEGIN IMMEDIATE'
    _popleft_get = (
            'SELECT id, item FROM queue '
            'ORDER BY id LIMIT 1'
            )
    _popleft_del = 'DELETE FROM queue WHERE id = ?'
    _peek = (
            'SELECT item FROM queue '
            'ORDER BY id LIMIT 1'
            )

    def __init__(self, path):
        self.path = os.path.abspath(path)
        self._connection_cache = {}
        with self._get_conn() as conn:
            conn.execute(self._create)

    def __len__(self):
        with self._get_conn() as conn:
            l = conn.execute(self._count).next()[0]
        return l

    def __iter__(self):
        with self._get_conn() as conn:
            for id, obj_buffer in conn.execute(self._iterate):
                yield loads(str(obj_buffer))

    def _get_conn(self):
        id = get_ident()
        if id not in self._connection_cache:
            self._connection_cache[id] = sqlite3.Connection(self.path, 
                    timeout=60)
        return self._connection_cache[id]

    def append(self, obj):
        '''
        Add an entry to the queue.
        @param obj: the entry to append to the queue
        @return: nothing
        Usage: $ python -mtimeit -s'from sqlite_queue import SqliteQueue; \
            from random import random; \
            q = SqliteQueue("/run/shm/queue")' 'q.append(random())'
        1000 loops, best of 3: 280 usec per loop
        '''
        obj_buffer = buffer(dumps(obj, 2))
        with self._get_conn() as conn:
            conn.execute(self._append, (obj_buffer,)) 

    def popleft(self, sleep_wait=True):
        '''
        Return the left-most entry after removing it from the queue.
        @param sleep_wait: true means sleep and try again if no entries
        @return: the entry or None
        usage: python -mtimeit -s'from sqlite_queue import SqliteQueue; \
            from random import random; \
            q = SqliteQueue("/run/shm/queue")' 'q.popleft()'
        1000 loops, best of 3: 325 usec per loop
        '''
        keep_pooling = True
        wait = 0.1
        max_wait = 2
        tries = 0
        with self._get_conn() as conn:
            id = None
            
            # Pole until an entry is found or
            # (end of entries and no sleep was requested).
            while keep_pooling:
                
                # Try to retrieve a queue entry and its ID.
                conn.execute(self._write_lock)
                cursor = conn.execute(self._popleft_get)
                try:
                    id, obj_buffer = cursor.next()
                    keep_pooling = False
                except StopIteration:
                
                    # We're at the end of the entries.
                    conn.commit() # unlock the database
                    
                    # We're done if no sleep was requested.
                    if not sleep_wait:
                        keep_pooling = False
                        continue
                    tries += 1
                    sleep(wait)
                    wait = min(max_wait, tries/10 + wait)
            if id:
            
                # Drop this entry from the queue.
                conn.execute(self._popleft_del, (id,))
                
                # Return the entry data.
                return loads(str(obj_buffer))
        return None

    def peek(self):
        with self._get_conn() as conn:
        
            # Retrieve a queue entry?
            cursor = conn.execute(self._peek)
            try:
                return loads(str(cursor.next()[0]))
            except StopIteration:
                return None

def queue_daemon(app, rv_ttl=500):
    '''
    An example from Thiago's message queue with redis.
    Modify this to work with sqlite.
    '''
    while 1:
        msg = redis.blpop(app.config['REDIS_QUEUE_KEY'])
        func, key, args, kwargs = loads(msg[1])
        try:
            rv = func(*args, **kwargs)
        except Exception, e:
            rv = e
        if rv is not None:
            redis.set(key, dumps(rv))
            redis.expire(key, rv_ttl)

'''
An example from Thiago's message queue with redis.
To run the daemon you can write a simple script like this:

#!/usr/bin/env python
from yourapp import app
from that_queue_module import queue_daemon
queue_daemon(app)
'''

