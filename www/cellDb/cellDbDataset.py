# The cell dataset database table access.

import os, traceback, csv
from dbTable import DbTable

class CellDbDataset(DbTable):

    # Sqlite database table templates.
    _dbCreate = (
        'CREATE TABLE IF NOT EXISTS dataset '
        '('
        '  id INTEGER PRIMARY KEY AUTOINCREMENT, '
        '  name text,'
        '  organ text,'
        '  species text,'
        '  sampleCount integer,'
        '  abnormality text,'
        '  primaryData text,'
        '  scanpyObjectOfPrimaryData text,'
        '  sampleMetadata text,'
        '  primaryDataNormalizationStatus text,'
        '  clusteringScript text,'
        '  reasonableForTrajectoryAnalysis text,'
        '  trajectoryAnalysisScript text,'
        '  platform text,'
        '  expressionDataSource text,'
        '  expressionDataSourceURL text'
        ')'
    )
    _dbPush = (
        'INSERT INTO dataset '
        '(name, organ, species, sampleCount, abnormality, primaryData, '
        '  scanpyObjectOfPrimaryData, sampleMetadata, '
        '  primaryDataNormalizationStatus, clusteringScript, '
        '  reasonableForTrajectoryAnalysis, trajectoryAnalysisScript, platform, '
        '  expressionDataSource, expressionDataSourceURL) '
        'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
    )

    def __init__(s, dbPath):

         # Connect to the database, creating if need be.
         s.dbPath = dbPath
         s.table = 'dataset'
         s._connection_cache = {}
         with s._getConnectionCache() as conn:
             conn.execute(s._dbCreate)


def getDbPath(appCtx):
    return os.path.join(appCtx.databasePath, 'cell.db')


def addMany(data, appCtx):

    # Add many rows to the database.
    # @param data: the new data as an array of arrays, one array per row
    #              in the form [name, organ, species, sampleCount, ...]
    # @param appCtx: the application context
    # @returns: nothing
    CellDbDataset(getDbPath(appCtx)).addMany(data)


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
    CellDbDataset(getDbPath(appCtx)).addManyFromFile(filePath)


def deleteAll(appCtx):

    # Clear the database of all data.
    # @param appCtx: the application context
    # @returns: nothing
     CellDbDataset(getDbPath(appCtx)).deleteAll()


def getAll(appCtx):

    # Dump all dataset info that is in the database.
    # @param appCtx: the application context
    # @returns: an array of dataset metadata in an object
    return CellDbDataset(getDbPath(appCtx)).getAll()
