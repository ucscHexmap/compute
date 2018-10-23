# The base class for database access.

import os, sqlite3, traceback

try:
    from thread import get_ident
except ImportError:
    from dummy_thread import get_ident


class DbBase(object):

    # Sqlite database templates.
    _dbDeleteAll = (
        'DELETE FROM db'
    )
    _dbGetAll = (
        'SELECT * FROM db'
    )
    _dbGetById = (
        'SELECT * FROM db '
        'WHERE id = ?'
    )
    _dbGetFirstRow = (
        'SELECT * FROM db '
        'LIMIT 1'
    )

    def _getConnection(s):

        # Get the sqlite connection for this thread where isolation_level=None
        # tells sqlite to commit automatically after each db update.
        return sqlite3.connect(s.dbPath, timeout=60, isolation_level=None)


    def _getConnectionCache(s):

        # Get the sqlite connection for this thread.
        # Any reads look at the cache first.
        id = get_ident()
        if id not in s._connection_cache:
            s._connection_cache[id] = s._getConnection()

        return s._connection_cache[id]


    def deleteAll(s):

        # Delete the entire database. Usually to reload data.
        with s._getConnectionCache() as conn:
            conn.execute(s._dbDeleteAll)


    def getAll(s, file=None):

        # Get all file information. Return it or write it to a file.
        with s._getConnectionCache() as conn:
            result = conn.execute(s._dbGetAll)
            if file:
                with open('dump.sql', 'w') as f:
                    for row in result:
                        f.write('%s\n' % row)
            else:
                rows = []
                for row in result:
                    rows.append(row)
                return rows


    def getOne (s, id):

        # Get the entire row for the given ID.
        with s._getConnectionCache() as conn:
            get = conn.execute(s._dbGetById, (id,))
            info = None
            for row in get:
                info = row
            return info


    def hasData(s):

        # Return true if there is at least one row in the db.
        with s._getConnectionCache() as conn:
            cursor = conn.execute(s._dbGetFirstRow)
            for row in cursor:
                return True
            return False
