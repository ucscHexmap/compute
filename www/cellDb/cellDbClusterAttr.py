
# The cell cluster database table access class.

import os, traceback, csv
from cellDbTableBase import CellDbTableBase

class CellDbClusterAttr(CellDbTableBase):

    table = 'clusterAttr'
    dbFileName = 'cell.db'

    # Sqlite database table templates.
    _dbCreate = (
        'CREATE TABLE IF NOT EXISTS ' + table + ' '
        '('
        '  id INTEGER PRIMARY KEY AUTOINCREMENT, '
        '  name text,'
        '  value text,'
        '  datasetId integer'
        ')'
    )
    _dbPush = (
        'INSERT INTO ' + table + ' '
        '(name, value, datasetId) '
        'VALUES (?,?,?)'
    )
