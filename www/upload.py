
# The upload API.

import os, traceback, datetime, json, importlib, logging
from util_web import Context, ErrorResp
from uploadDb import UploadDb

# TODO can use set the db path just once and not include it in all of the
# below calls?

def add (email, group, name, size, uploadPath, db):

    # Add a file's information.
    #
    # @param      email: an email address as owner of files and results
    # @param      group: an access group or clean email/username
    # @param       name: user's basename of file
    # @param       size: size in bytes
    # @param uploadPath: absolute path to the upload directory
    # @param         db: database instance
    # @returns: uploadId
    print 'db:', db
    print 'email, group, name, size:', email, group, name, size
    uploadId = UploadDb(db).add(email, group, name, size, uploadPath)
    return { uploadId: uploadId }


def getAll (uploadPath, db):

    # Get all upload information of files in the upload area.
    #
    # @param uploadPath: absolute path to the upload directory
    # @param         db: database instance
    # @returns: an array of uploadInfo in an object
    return { 'uploadInfo': UploadDb(db).getAll(uploadPath) }


def getGroupFiles (group, uploadPath, db):

    # Retrieve the file information for a group or user.
    #
    # @param      group: the access group or clean email/username
    # @param uploadPath: absolute path to the upload directory
    # @param         db: database instance
    # @returns: a dict of information for this groups files.
    return UploadDb(db).getGroupFiles(group, uploadPath)


def getPublicFiles (uploadPath, db):

    # Retrieve the file information for a group or user.
    #
    # @param      group: the access group or clean email/username
    # @param uploadPath: absolute path to the upload directory
    # @param         db: database instance
    # @returns: a dict of information for this groups files.
    return UploadDb(db).getPublicFiles(uploadPath)


def updateFormat (id, format, uploadPath, db):

    # Update a file's format.
    #
    # @param         id: an access group or clean email/username
    # @param     format: file format
    # @param uploadPath: absolute path to the upload directory
    # @param         db: database instance
    # @returns: nothing
    
    UploadDb(db).updateFormat(id, format, uploadPath)


def updateStatus (id, status, uploadPath, db):

    # Update a file upload status.
    #
    # @param         id: an access group or clean email/username
    # @param     status: a valid status
    # @param uploadPath: absolute path to the upload directory
    # @param         db: database instance
    # @returns: nothing
    
    UploadDb(db).updateFormat(id, status, uploadPath)
