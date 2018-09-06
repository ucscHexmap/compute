
# The upload info data base access.


import os, sqlite3, traceback, datetime, json
try:
    from thread import get_ident
except ImportError:
    from dummy_thread import get_ident
import validate_web

class UploadDb(object):
    '''
    # Status constants.
    canceledSt = 'Canceled'
    errorSt = 'Error'
    timeoutSt = 'Timeout'
    successSt = 'Success'
    uploadingSt = 'Uploading'
    
    # Format constants.
    featureMatrix = 'featureMatrix'
    fullSim = 'fullSimilarity'
    metadata = 'metadata'
    sparseSim = 'sparseSimilarity'
    tbd = 'tbd'
    trajectory = 'trajectory'
    xyPos = 'xyPositions'
    
    # Column index constants.
    idI = 0       # unique upload info identifier
    baseNameI = 1 # file-safe base name we assign
    dateI = 2     # date in ISO format: yyyy-mm-dd
    emailI = 3    # an email address as owner of files and results
    formatI = 4   # file format, one of the above format constants
    groupI = 5    # an access group or clean email/username
    nameI = 6     # user's base name of the file
    sizeI = 7     # size in bytes
    statusI = 8   # status of the upload, one of the above
    '''
    # Sqlite database access.
    _dbCreate = (
        'CREATE TABLE IF NOT EXISTS db '
        '('
        '  id INTEGER PRIMARY KEY AUTOINCREMENT'
        ')'
    )
    '''
        '  baseName text,'
        '  date text,'
        '  email text,'
        '  format text,'
        '  group text,'
        '  name text,'
        '  size integer,'
        '  status text'
    '''
    '''
    _dbPush = (
        'INSERT INTO db '
        '(baseName, date, email, format, group, name, size, status) '
        'VALUES (?, ?, ?, ?, ?)'
    )
    _dbGetById = (
        'SELECT * FROM db '
        'WHERE id = ?'
    )
    _dbGetByGroup = (
        'SELECT * FROM db '
        'WHERE group = ? '
        'ORDER BY date'
    )
    _dbGetAll = (
        'SELECT * FROM db '
        'ORDER BY id'
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
    '''

    def getConnection (s):
    
        # Get the sqlite connection for this thread where isolation_level=None
        # tells sqlite to commit automatically after each db update.
        # TODO: why do some calls use this and some use the cache?
        return sqlite3.connect(s.dbPath, timeout=60, isolation_level=None)
    
    
    def _getConn (s):
    
        # Get the sqlite connection for this thread.
        id = get_ident()
        if id not in s._connection_cache:
            s._connection_cache[id] = s.getConnection()

        return s._connection_cache[id]

    '''
    def _today (s):
    
        # Today formatted as yyyy-mm-dd.
        return datetime.date.today()
    '''

    def __init__(s, dbPath):
    
        # Connect to the database, creating if need be.
        s.dbPath = dbPath
        print 's.dbPath:', s.dbPath
        s._connection_cache = {}
        with s._getConn() as conn:
            conn.execute(s._dbCreate)

    '''
    def _getOne (s, id):

        # Get the entire row for the given ID.
         with s._getConn() as conn:
            get = conn.execute(s._dbGetById, (id,))
            job = None
            for row in get:
                job = row
            return job


    def add (s, email, group, name, size, uploadPath):
    
        # Add a file's info to the database.
        basename = validate_web.cleanFileName(name)
        date = s._today()
        format = 'TBD'

        with s._getConn() as conn:
            curs = conn.cursor()
            curs.execute(s._dbPush, (baseName, date, email, format, group, name, size, s.uploadingSt,))
            return curs.lastrowid


    def delete (s, id, uploadPath):
    
        # Remove a file and it's information.
        with s.getConnection() as conn:
            conn.execute(s._dbRemoveById, (id,))


    def getAll (s, uploadPath):
    #def getAll (s, uploadPath, file=None):

        # Get every row in the database, writing to a file, or to memory.
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


    def getGroupFiles (s, group, uploadPath):
        
        # Get every row in the database, writing to a file, or to memory.
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


    def getPublicFiles (s, uploadPath):
        
        # Get every row in the database, writing to a file, or to memory.
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


    def updateFormat (s, id, format, uploadPath):
    
        # Update a file's format.
        with s.getConnection() as conn:
            conn.execute(s._dbSetFormat, (format,))


    def updateStatus (s, id, status, uploadPath):
    
        # Update a file upload status.
        with s.getConnection() as conn:
            conn.execute(s._dbSetStatus, (status,))
    '''
