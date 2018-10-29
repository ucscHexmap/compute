# The cell dataset database table access.

import os, traceback, csv
from cellDbTableBase import CellDbTableBase

class CellDbDataset(CellDbTableBase):

    table = 'dataset'
    dbFileName = 'cell.db'

    # Sqlite database table templates.
    _dbCreate = (
        'CREATE TABLE IF NOT EXISTS ' + table + ' '
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
        'INSERT INTO ' + table + ' '
        '(name, organ, species, sampleCount, abnormality, primaryData, '
        '  scanpyObjectOfPrimaryData, sampleMetadata, '
        '  primaryDataNormalizationStatus, clusteringScript, '
        '  reasonableForTrajectoryAnalysis, trajectoryAnalysisScript, platform, '
        '  expressionDataSource, expressionDataSourceURL) '
        'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
    )
