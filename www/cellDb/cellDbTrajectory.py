
# The cell trajectory database table access.

import os, traceback, csv
from cellDbTableBase import CellDbTableBase

class CellDbTrajectory(CellDbTableBase):

    table = 'trajectory'
    dbFileName = 'cell.db'

    # Sqlite database table templates.
    _dbCreate = (
        'CREATE TABLE IF NOT EXISTS ' + table + ' '
        '('
        '  id INTEGER PRIMARY KEY AUTOINCREMENT, '
        '  name text,'
        '  digitId integer,'
        '  datasetId integer'
        ')'
    )
    _dbPush = (
        'INSERT INTO ' + table + ' '
        '(name, digitId, datasetId) '
        'VALUES (?,?,?)'
    )
