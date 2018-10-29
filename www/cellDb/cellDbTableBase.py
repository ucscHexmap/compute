
# The base class for database table access.
# This handles simple single table operations where the columns do not need to
# be known.

import os, sqlite3, traceback, csv

try:
    from thread import get_ident
except ImportError:
    from dummy_thread import get_ident


class CellDbTableBase(object):

    def __init__(s, dbPath):

         # Connect to the database, creating if need be.
         s.dbPath = dbPath
         s._connection_cache = {}
         with s._getConnectionCache() as conn:
             conn.execute(s._dbCreate)


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


    def _pushOne(s, row, conn):
        cursor = conn.cursor()
        cursor.execute(s._dbPush, row)
        return cursor


    def addMany(s, data):

        # Add many rows to the table.
        # @param data: the new data as an array of arrays, one array per row
        #              in the form [<value>, <value>, <value>, ...]
        # @returns: nothing
        with s._getConnectionCache() as conn:
            for row in data:
                s._pushOne(row, conn)


    def addManyFromFile(s, filePath, replace=False):

        # Add many rows from a file to the table.
        # @param filePath: the full path to the file
        #                  where the file is TSV with one row per dataset
        # @param replace: True to replace all rows, False to append
        # @returns: nothing
        if replace:
            s.deleteAll()
        with s._getConnectionCache() as conn:
            with open(filePath, 'r') as f:
                f = csv.reader(f, delimiter='\t')
                for row in f:
                    s._pushOne(row, conn)


    def addOne(s, row):

        # Add one row.
        with s._getConnectionCache() as conn:
             cursor = s._pushOne(row, conn)
        return cursor.lastrowid


    def deleteAll(s):

        # Clear the table of all data, usually to reload the table.
        # @returns: nothing
        with s._getConnectionCache() as conn:
            conn.execute('DELETE FROM ' + s.table)


    def getAll(s, file=None):

        # Get all rows that are in the table.
        # @returns: an array of table rows in an object if not written to file
        with s._getConnectionCache() as conn:
            result = conn.execute('SELECT * FROM ' + s.table)
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
            get = conn.execute(
                'SELECT * FROM ' + s.table + ' WHERE id = ' + str(id))
            info = None
            for row in get:
                info = row
        return info


    def hasData(s):

        # Return true if there is at least one row in the table.
        with s._getConnectionCache() as conn:
            cursor = conn.execute('SELECT * FROM ' + s.table + ' LIMIT 1')
            for row in cursor:
                return True
        return False

