
# The cell dataset API.

import os, traceback, csv
from cellDatasetDb import CellDatasetDb


def addMany(data, dbPath):

    # Add many rows to the database.
    # @param data: the new data as an array of arrays, one array per row
    #              in the form [name, organ, species, sampleCount, ...]
    # @param dbPath: the database path
    # @returns: nothing
    CellDatasetDb(dbPath).addMany(data)


def addManyFromFile(filePath, dbPath, replace=False):

    # Add many rows from a file to the database.
    # @param filePath: the path to the file (TODO: full path?)
    #                  where the file is TSV with one row per dataset
    #                  in the form [name, organ, species, sampleCount, ...]
    # @param dbPath: the database path
    # @param replace: True to replace all rows, False to append.
    # @returns: nothing
    if replace:
        deleteAll(dbPath)
    CellDatasetDb(dbPath).addManyFromFile(filePath)


def deleteAll(dbPath):

    # Clear the database of all data.
    # @param dbPath: the database path
    # @returns: nothing
     CellDatasetDb(dbPath).deleteAll()


def getAll(dbPath):

    # Dump all dataset info that is in the database.
    # @param dbPath: the database path
    # @returns: an array of dataset metadata in an object
    return {'datasetInfo': CellDatasetDb(dbPath).getAll()}
