# The cell dataset data base access.

import os, traceback, csv
from dbBase import DbBase


class CellDatasetDb(DbBase):

    '''
    name
    organ
    species
    sample count
    abnormality
    "primary data"
    "scanpy object of primary data"
    sample metadata
    primary data normalization status
    clustering script
    reasonable for trajectory analysis
    trajectory analysis script
    platform
    expression data source
    expression data source URL
    '''

    # Sqlite database templates.
    _dbCreate = (
        'CREATE TABLE IF NOT EXISTS db '
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
        'INSERT INTO db '
        '(name, organ, species, sampleCount, abnormality, primaryData, '
        '  scanpyObjectOfPrimaryData, sampleMetadata, '
        '  primaryDataNormalizationStatus, clusteringScript, '
        '  reasonableForTrajectoryAnalysis, trajectoryAnalysisScript, platform, '
        '  expressionDataSource, expressionDataSourceURL) '
        'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
    )
