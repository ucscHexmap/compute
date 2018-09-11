
# The upload info data base access.


import os, sqlite3, traceback, datetime, json
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
    
    # Column index constants.
    idI = 0        # unique upload info identifier
    authGroupI = 1 # an access group or clean email/username
    baseNameI = 2  # file-safe base name we assign
    dateI = 3      # date in ISO format: yyyy-mm-dd
    emailI = 4     # an email address as owner of files and results
    formatI = 5    # file format, one of the above format constants
    nameI = 6      # user's base name of the file
    sizeI = 7      # size in bytes
    statusI = 8    # status of the upload, one of the above
    
    # Sqlite database access.
    _dbCreate = (
        'CREATE TABLE IF NOT EXISTS db '
        '('
        '  id INTEGER PRIMARY KEY AUTOINCREMENT,'
        '  authGroup text,'
        '  baseName text,'
        '  date text,'
        '  email text,'
        '  format text,'
        '  name text,'
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
        '(authGroup, baseName, date, email, format, name, size, status) '
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
    
        # Today formatted as yyyy-mm-dd.
        return datetime.date.today()


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
        with s._getConnectionCache() as conn:
            curs = conn.cursor()
            curs.execute(s._dbPush, (
                authGroup,
                validate_web.cleanFileName(name),
                s._today(),
                email,
                s.tbd,
                name,
                size,
                s.uploading))
            return curs.lastrowid


    def hasData (s):
    
        # Return true if there is at least on row in the db.
        with s._getConnectionCache() as conn:
            cursor = conn.execute(s._dbGetFirstRow)
            for row in cursor:
                return True
            return False


    def delete (s, id):
        with s._getConnectionCache() as conn:
            conn.execute(s._dbRemoveById, (id,))


    def getAll (s, file=None):
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
        with s._getConnectionCache() as conn:
            conn.execute(s._dbSetFormat, (format, id,))


    def updateStatus (s, id, status):
        with s._getConnectionCache() as conn:
            conn.execute(s._dbSetStatus, (status, id,))

