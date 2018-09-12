
# The upload info data base access.


import os, sqlite3, traceback, json
from datetime import date
try:
    from thread import get_ident
except ImportError:
    from dummy_thread import get_ident
import validate_web

class UploadDb(object):
    
    # Status constants.
    canceled = 'Canceled'
    error = 'Error'
    timeout = 'Timeout'
    success = 'Success'
    uploading = 'Uploading'
    
    # Format constants.
    featureMatrix = 'featureMatrix'
    fullSim = 'fullSimilarity'
    metadata = 'metadata'
    sparseSim = 'sparseSimilarity'
    tbd = 'TBD'
    trajectory = 'trajectory'
    xyPos = 'xyPositions'
    
    # Column name constants.
    prop = [
        'id',
        'authGroup',
        'date',
        'email',
        'format',
        'name',
        'safeName',
        'size',
        'status'
    ]
    
    # Column index constants.
    idI = 0        # unique upload info identifier
    authGroupI = 1 # an access group or clean email/username
    dateI = 2      # date in ISO format: yyyy-mm-dd
    emailI = 3     # an email address as owner of files and results
    formatI = 4    # file format, one of the above format constants
    nameI = 5      # user's base name of the file
    safeNameI = 6  # file-safe name we assign
    sizeI = 7      # size in bytes
    statusI = 8    # status of the upload, one of the above

    # Sqlite database templates.
    _dbCreate = (
        'CREATE TABLE IF NOT EXISTS db '
        '('
        '  id INTEGER PRIMARY KEY AUTOINCREMENT,'
        '  authGroup text,'
        '  date text,'
        '  email text,'
        '  format text,'
        '  name text,'
        '  safeName text,'
        '  size integer,'
        '  status text'
        ')'
    )
    _dbGetAll = (
        'SELECT * FROM db '
        'ORDER BY date'
    )
    _dbGetByGroup = (
        'SELECT * FROM db '
        'WHERE authGroup = ? '
        'ORDER BY date'
    )
    _dbGetById = (
        'SELECT * FROM db '
        'WHERE id = ?'
    )
    _dbGetFirstRow = (
        'SELECT * FROM db '
        'LIMIT 1'
    )
    _dbPush = (
        'INSERT INTO db '
        '(authGroup, date, email, format, name, safeName, size, status) '
        'VALUES (?,?,?,?,?,?,?,?)'
    )
    _dbRemoveById = (
        'DELETE FROM db '
        'WHERE id = ?'
    )
    _dbSetFormat = (
        'UPDATE db '
        'SET format = ? '
        'WHERE id = ?'
    )
    _dbSetStatus = (
        'UPDATE db '
        'SET status = ? '
        'WHERE id = ?'
    )


    def _getConnection (s):
    
        # Get the sqlite connection for this thread where isolation_level=None
        # tells sqlite to commit automatically after each db update.
        return sqlite3.connect(s.dbPath, timeout=60, isolation_level=None)

    
    def _getConnectionCache (s):
    
        # Get the sqlite connection for this thread.
        # Any reads look at the cache first.
        id = get_ident()
        if id not in s._connection_cache:
            s._connection_cache[id] = s._getConnection()

        return s._connection_cache[id]


    def _today (s):
    
        # Today in ISO format as a string of the form, yyyy-mm-dd.
        return date.today().isoformat()



    def __init__(s, dbPath):
    
        # Connect to the database, creating if need be.
        s.dbPath = dbPath
        s._connection_cache = {}
        with s._getConnectionCache() as conn:
            conn.execute(s._dbCreate)


    def _getOne (s, id):

        # Get the entire row for the given ID.
         with s._getConnectionCache() as conn:
            get = conn.execute(s._dbGetById, (id,))
            info = None
            for row in get:
                info = row
            return info


    def addOne (s, authGroup, name, size, email=None):
    
        # Add one file's information.
        with s._getConnectionCache() as conn:
            curs = conn.cursor()
            curs.execute(s._dbPush, (
                authGroup,
                s._today(),
                email,
                s.tbd,
                name,
                validate_web.cleanFileName(name),
                size,
                s.uploading))
            return curs.lastrowid


    def hasData (s):
    
        # Return true if there is at least one row in the db.
        with s._getConnectionCache() as conn:
            cursor = conn.execute(s._dbGetFirstRow)
            for row in cursor:
                return True
            return False


    def delete (s, id):
    
        # Delete a file's info given a row ID.
        with s._getConnectionCache() as conn:
            conn.execute(s._dbRemoveById, (id,))


    def getAll (s, file=None):
        
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


    def getGroupFiles (s, authGroup, file=None):
        
        # Get a group's file information. Return it or write it to a file.
        with s._getConnectionCache() as conn:
            result = conn.execute(s._dbGetByGroup, (authGroup,))
            if file:
                with open('dump.sql', 'w') as f:
                    for row in result:
                        f.write('%s\n' % row)
            else:
                rows = []
                for row in result:
                    rows.append(row)
                return rows


    def getPublicFiles (s, file=None):
        
        # Get the public file information. Return it or write it to a file.
        with s._getConnectionCache() as conn:
            result = conn.execute(s._dbGetByGroup, ('public',))
            if file:
                with open('dump.sql', 'w') as f:
                    for row in result:
                        f.write('%s\n' % row)
            else:
                rows = []
                for row in result:
                    rows.append(row)
                return rows


    def updateFormat (s, id, format):
    
        # Update the format given a row ID.
        with s._getConnectionCache() as conn:
            conn.execute(s._dbSetFormat, (format, id,))


    def updateStatus (s, id, status):
    
        # Update the status given a row ID.
        with s._getConnectionCache() as conn:
            conn.execute(s._dbSetStatus, (status, id,))


    def loadInitial(s, data):
    
        # Load data into the database when it is empty.
        with s._getConnectionCache() as conn:
            for r in data:
                curs = conn.cursor()
                curs.execute(s._dbPush, (
                    r[s.authGroupI-1],
                    r[s.dateI-1],
                    r[s.emailI-1],
                    r[s.formatI-1],
                    r[s.nameI-1],
                    r[s.safeNameI-1],
                    r[s.sizeI-1],
                    r[s.statusI-1],
                ))
