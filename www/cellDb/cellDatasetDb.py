# The cell dataset data base access.

import os, traceback, csv
from dbBase import DbBase


class CellDatasetDb(DbBase):

    # Column name constants.
    prop = [
        'id',
        'name',
        'organ',
        'species',
        'sampleCount',
    ]

    # Column index constants.
    idI = 0  # dataset ID unique to database
    nameI = 1  # dataset name
    organI = 2  #
    speciesI = 3  #
    sampleCountI = 4  #

    # Sqlite database templates.
    _dbCreate = (
        'CREATE TABLE IF NOT EXISTS db '
        '('
        '  id INTEGER PRIMARY KEY AUTOINCREMENT,'
        '  name text,'
        '  organ text,'
        '  species text,'
        '  sampleCount integer'
        ')'
    )
    _dbPush = (
        'INSERT INTO db '
        '(name, organ, species, sampleCount) '
        'VALUES (?,?,?,?)'
    )


    def __init__(s, dbPath):

        # Connect to the database, creating if need be.
        s.dbPath = dbPath
        s._connection_cache = {}
        with s._getConnectionCache() as conn:
            conn.execute(s._dbCreate)


    def addMany(s, data):
        # Load more than one row of data to the database.
        with s._getConnectionCache() as conn:
            for r in data:
                curs = conn.cursor()
                curs.execute(s._dbPush, (
                    r[s.nameI - 1],
                    r[s.organI - 1],
                    r[s.speciesI - 1],
                    r[s.sampleCountI - 1]
                ))


    def addManyFromFile(s, filePath):

        # Load data from a tsv file .
        with s._getConnectionCache() as conn:

            with open(filePath, 'r') as f:
                f = csv.reader(f, delimiter='\t')
                for r in f:
                    curs = conn.cursor()
                    curs.execute(s._dbPush, (
                        r[s.nameI - 1],
                        r[s.organI - 1],
                        r[s.speciesI - 1],
                        r[s.sampleCountI - 1]
                    ))


    def addOne(s, name, organ, species, sampleCount):

        # Add one row.
        with s._getConnectionCache() as conn:
            curs = conn.cursor()
            curs.execute(s._dbPush, (
                name,
                organ,
                species,
                sampleCount
            ))
        return curs.lastrowid


