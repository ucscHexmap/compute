
# The upload API.

import os, traceback, datetime, json, importlib, logging
from util_web import Context, ErrorResp
from uploadDb import UploadDb

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
    return list(files) + list(dirs)


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


def _getFileData(uploadPath, major, file, minor=None):

    # Build the data for one file.
    # Get the file stats.
    stat = os.stat(os.path.join(uploadPath, major, minor, filePath))
    
    # TODO: basename is not really a basename any more due to the minor dir.
    name = os.path.join(minor, filePath)

    data = [
        major,                   # authGroup
        name,                    # baseName
        strftime("%Y-%m-%d", stat.st_mtime), # date
        _getEmail(major),        # email
        UploadDb(dbPath).tbd,    # format
        name,                    # name
        stat.st_size,            # size
        UploadDb(dbPath).success # status
    ]
    return data


def _getAllData (uploadPath):

    # Get the data for all uploaded files.
    # @param uploadPath: absolute path to the upload directory
    # @returns: data for all uploaded files.

    # Get the major directory names.
    majors = _getSubDirs(uploadPath)
    
    # Loop through the majors.
    for major in majors:

        # Get immediate dirs and files of the major dir.
        filesDirs = _getFilesDirs(os.path.join(rootDir, major))
        
        # Add data for the files in this major dir.
        for file in filesDirs[2]:
            data.append(_getFileData(uploadPath, major, file))

        # Add data for the files in each of the subdirs of the major dir.
        for minor in filesDirs[1]:
            files = _getFiles(os.path.join(rootDir, major, minor))
            for file in files:
                data.append(_getFileData(uploadPath, major, file, minor))

    return data


def _loadDb (uploadPath, dbPath):

    # Populate the data for all uploaded files into a new database.
    # @param uploadPath: absolute path to the upload directory
    # @param     dbPath: database path
    # @returns: nothing
    data = _getAllData(uploadPath)

    # TODO: update the database


def _verifyDb (uploadPath, dbPath):

    # Compare the actual file data to the database.
    # @param uploadPath: absolute path to the upload directory
    # @param     dbPath: database path
    # @returns: nothing
    data = _getAllData(uploadPath)

    # TODO: compare to the database.


def initialize (uploadPath, dbPath):

    # Initialize the database. If the db file exists, it's contents are compared
    # to the files in the upload directory. If the db does not exist it is built
    # from the upload directory.
    #
    # @param uploadPath: absolute path to the upload directory
    # @param     dbPath: database path
    # @returns: nothing
    if UploadDb(dbPath).hasData():
        _verifyDb(uploadPath, dbPath)
    else:
        _loadDb(uploadPath, dbPath)

