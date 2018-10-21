
# Handle uploading of files.

import os
from flask import Flask, request
import uploadDb
from util_web import ErrorResp, getAppCtx
import validate_web as validate


def oldApi (dataId, request):
    
    # If the client does not include a file property in the post
    # there is nothing to upload. So bail.
    if 'file' not in request.files:
        raise ErrorResp('No file property provided for upload', 400)
    
    file = request.files['file']

    # If a browser user does not select a file, the browser submits an
    # empty file property. So bail.
    if file.filename == '':
        raise ErrorResp('No file provided for upload', 400)

    filename = validate.cleanFileName (file.filename)

    appCtx = getAppCtx()
    path = os.path.join(appCtx.dataRoot, dataId)
    
    # Make the directories if they are not there.
    try:
        os.makedirs(path[:path.rfind('/')], 0770)
    except Exception:
        pass

    # Save the file
    try:
        file.save(path)
    except Exception:
        raise ErrorResp('Unable to save file: ' + filename, 500)
    
    return filename


def _validateUploadFile(data, request):

    # If the client does not include a file property in the post
    # there is nothing to upload. So bail.
    if 'file' not in request.files:
        raise ErrorResp('No file property provided for upload', 400)

    # If a browser user does not select a file, the browser submits an
    # empty file property. So bail.
    fileObj = request.files['file']
    if fileObj.filename == '':
        raise ErrorResp('No file provided for upload', 400)

    validate.emailSingleRequired(data)
    validate.token(data)
    validate.authGroup(data)
    validate.major(data)
    validate.minor(data)

    # Remove any strange characters from the fileName
    cleanFileName = validate.cleanFileName(file.filename)
    return (cleanFileName, fileObj)


def _addDb (email, authGroup, major, minor, fileName, size, db):
    id = db.addOne(authGroup, fileName, major, minor, size, email)
    return id


def _saveFile (fileObj, major, minor, fileName, uploadPath):

    # Make the full path to save the file.
    path = makeFullPath(major, fileName, minor, uploadPath)
    
    # Make the directories if they are not there, read/writable by group.
    try:
        os.makedirs(path[:path.rfind('/')], 0770)
    except Exception:
        pass

    # Save the file.
    try:
        fileObj.save(path)
    except Exception(error):
        return ('error', error)
        db.updateStatus(id, db.error)
        raise ErrorResp('Unable to save file: ' + fileName, 500)

    return ('success', None)


def _auth (email, token, appCtx):

    # Authenticate and authorize with the view server.
    url = appCtx.viewServer + '/auth' + \
        '/email/' + email + \
        '/token/' + token

    # TODO


def add (email, token, authGroup, major, minor, request):

    # Add a file to the upload directory and its info to the database.
    print '### uploadFile.add()'

    # Validate parms and clean the file name.
    (fileName, fileObj) = _validateUploadFile({
        'email': email,
        'token': token,
        'authGroup': authGroup,
        'major': major,
        'minor': minor,
    }, request)

    # Authenticate and authorize.
    appCtx = getAppCtx()
    _auth(email, token, appCtx)

    # Add the file info to the database.
    db = UploadDb(appCtx.uploadDbPath)
    id = _addDb (email, authGroup, major, minor, fileName, fileObj.size, db)

    # Save the file.
    (status, msg) = _saveFile(
        fileObj, major, minor, fileName, ctx.uploadFilePath)

    # Update the database status.
    if status == 'success':
        db.updateStatus(id, db.success)
    else:
        db.updateStatus(id, db.error)
        raise ErrorResp('Unable to save file: ' + fileName + ': ' + msg, 500)

    return (id, fileName) # TODO: do we need the ID here?

