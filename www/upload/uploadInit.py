
# The upload API.

import os, traceback, datetime, json, importlib, logging
from datetime import date
from util_web import Context, ErrorResp
from uploadDb import UploadDb
from util_web import sendAdminEmail

def _getSubDirs (path):

    # Get immediate sub directories, removing any hidden dirs.
    allSubDirs = next(os.walk(path))[1]
    subDirs = filter(lambda x: x[0] != '.', allSubDirs)
    return list(subDirs)


def _getFilesDirs (path):

    # Get immediate sub directories and files, removing any hidden dirs/files.
    allFilesDirs = next(os.walk(path))
    dirs = filter(lambda x: x[0] != '.', allFilesDirs[1])
    files = filter(lambda x: x[0] != '.', allFilesDirs[2])
    return { 'files': list(files), 'dirs': list(dirs) }


def _getFiles (path):

    # Get immediate sub files, removing any hidden files.
    allFiles = next(os.walk(path))[2]
    files = filter(lambda x: x[0] != '.', allFiles)
    return list(files)


def _getEmail(major):
    
    # Construct an email address if possible.
    # a_b.c -> a@b.c
    email = None
    index = major.find('_', 1, len(major)-3)
    if index > 0:
        email = major.replace('_', '@', 1)
    return email


def _getFileData(major, file, uploadPath, dbPath, minor=None):

    # Build the data for one file.
    # Get the file stats.
    path = os.path.join(uploadPath, major)
    if minor == None:
        path = os.path.join(path, file)
        name = file
    else:
        path = os.path.join(path, minor, file)
        # TODO: basename is not really a basename any more due to the minor dir.
        name = os.path.join(minor, file)

    # Get the file stats.
    stat = os.stat(path)

    db = UploadDb(dbPath)
    data = [
        major,            # authGroup
        date.fromtimestamp(stat.st_mtime).isoformat(), # date
        _getEmail(major), # email
        db.tbd,           # format
        name,             # name
        name,             # safeName
        stat.st_size,     # size
        db.success        # status
    ]
    return data


def _getAllData (uploadPath, dbPath):

    # Get the data for all uploaded files.
    #
    # @param uploadPath: absolute path to the upload directory
    # @returns: data for all uploaded files.

    # Get the major directory names.
    majors = _getSubDirs(uploadPath)

    # Loop through the majors.
    data = []
    for major in majors:

        # Get immediate dirs and files of the major dir.
        filesDirs = _getFilesDirs(os.path.join(uploadPath, major))
        
        # Add data for the files in this major dir.
        for file in filesDirs['files']:
            data.append(_getFileData(major, file, uploadPath, dbPath))

        # Add data for the files in each of the subdirs of the major dir.
        for minor in filesDirs['dirs']:
            files = _getFiles(os.path.join(uploadPath, major, minor))
            for file in files:
                data.append(
                    _getFileData(major, file, uploadPath, dbPath, minor))

    return data


def _loadDb (uploadPath, dbPath):

    # Populate the data for all uploaded files into a new database.
    #
    # @param uploadPath: absolute path to the upload directory
    # @param     dbPath: database path
    # @returns: nothing
    data = _getAllData(uploadPath, dbPath)
    UploadDb(dbPath).loadInitial(data)


def _compareActualFileToDb (a, d, db):

    # Compare a file's actual info to the database.
    #
    # @param    a: actual info for a file as a tuple
    # @param    d: file info according to the db as a tuple
    # @param diff: the existing diff list
    # @param   db: the db instance
    # @returns: updated diff list

    # For each property value in the db info for this file...
    rowDiff = [d[db.authGroupI] + '/' + d[db.safeNameI] + \
        ': prop: actual, db:']
    for j, aVal in enumerate(a):
        i = j+1 # don't compare to db id, which actual file doesn't have
        if d[i] != aVal:
        
            # Record the diff.
            rowDiff.append(
                '  ' + db.prop[i] + ': ' + str(aVal) + ', ' + str(d[i])
            )

    # If there are any row diffs, return them
    if len(rowDiff) > 1:
        return rowDiff
    return []


def _compareAllActualToDb (actualInfo, dbInfo, db):

    # Compare the actual file info to the database.
    #
    # @param actualInfo: derived by examining each file
    # @param     dbInfo: file info according to the db
    # @param         db: the db instance
    # @returns: a diff list

    # Find each actual file in the db.
    diff = []
    for a in actualInfo:

        # Find this actual file in the db.
        # The actual info indexing is one less than the db due to no ID.
        found = None
        for d in dbInfo:
            if d[db.authGroupI] == a[db.authGroupI-1] and \
                d[db.safeNameI] == a[db.safeNameI-1]:
                
                found = d
                break
        #print 'd:', d
        if found:
            diff.extend(_compareActualFileToDb(a, found, db))
        else:

            # Record the fact there is no matching db row.
            diff.append(a[db.authGroupI-1] + '/' + a[db.safeNameI-1] + \
                ': file not in DB')
    
    return diff


def _dbEntriesWithoutFiles (actualInfo, dbInfo, db):

    # Compare the actual file info to the database.
    #
    # @param actualInfo: derived by examining each file
    # @param     dbInfo: file info according to the db
    # @param         db: the db instance
    # @returns: updated diff list

    # Find db info where there is no file.
    diff = []
    for d in dbInfo:

        # Find this db info's actual file.
        found = False
        for a in actualInfo:
            if (d[db.authGroupI] == a[db.authGroupI-1] and \
                d[db.safeNameI] == a[db.safeNameI-1]):
                
                found = True
                break
        if not found:
            diff.append(d[db.authGroupI] + '/' + d[db.safeNameI] + \
                ': DB entry without actual file')

    return diff


def _compareActualAndDb (uploadPath, dbPath):

    # Compare the actual file info to that in the DB.
    #
    # @param uploadPath: absolute path to the upload directory
    # @param     dbPath: database path
    # @returns: a diff list

    db = UploadDb(dbPath)
    dbInfo = db.getAll()
    actualInfo = _getAllData(uploadPath, dbPath)
    diff = _compareAllActualToDb(actualInfo, dbInfo, db)
    diff.extend(_dbEntriesWithoutFiles(actualInfo, dbInfo, db))

    return diff


def mailDiff (diff, appCtx):
    if len(diff) < 1:
        return
    subject = ''
    if appCtx.dev == 1:
        subject = 'DEV: '
    subject += 'diffs between upload DB and actual files'

    body = ''
    for d in diff:
        body += (d + '\n')
    sendAdminEmail(subject, body, appCtx)

def initialize (appCtx):

    # Initialize the upload module.
    #
    # @param appCtx: application context
    # @returns: nothing
    
    # Pull out the upload file directory and where the db is stored.
    uploadPath = appCtx.uploadPath
    dbPath = appCtx.uploadDbPath
    
    # If the database exists with data...
    if UploadDb(dbPath).hasData():
        
        # Compare actual file info with the db.
        diff = _compareActualAndDb(uploadPath, dbPath)
        mailDiff(diff, appCtx)
    else:
    
        # Build the db from the existing files.
        _loadDb(uploadPath, dbPath)

