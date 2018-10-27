
# The cell dataset API.

import os, traceback, csv
from cellDatasetDb import CellDatasetDb


def getDbPath(appCtx):
    return os.path.join(appCtx.databasePath, 'datasetDb.db')


def addMany(data, appCtx):

    # Add many rows to the database.
    # @param data: the new data as an array of arrays, one array per row
    #              in the form [name, organ, species, sampleCount, ...]
    # @param appCtx: the application context
    # @returns: nothing
    CellDatasetDb(getDbPath(appCtx)).addMany(data)


def addManyFromFile(filePath, appCtx, replace=False):

    # Add many rows from a file to the database.
    # @param filePath: the full path to the file
    #                  where the file is TSV with one row per dataset
    #                  in the form [name, organ, species, sampleCount, ...]
    # @param appCtx: the application context
    # @param replace: True to replace all rows, False to append.
    # @returns: nothing
    if replace:
        deleteAll(appCtx)
    CellDatasetDb(getDbPath(appCtx)).addManyFromFile(filePath)


def deleteAll(appCtx):

    # Clear the database of all data.
    # @param appCtx: the application context
    # @returns: nothing
     CellDatasetDb(getDbPath(appCtx)).deleteAll()


def getAll(appCtx):

    # Dump all dataset info that is in the database.
    # @param appCtx: the application context
    # @returns: an array of dataset metadata in an object
    return CellDatasetDb(getDbPath(appCtx)).getAll()
