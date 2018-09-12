#!/usr/bin/env python2.7

# This tests the upload logic between routes and the database.

import os
from datetime import date
import json
from util_web import Context
import unittest
import testUtil as util
import uploadInit
from uploadDb import UploadDb

#testDir = os.path.join(os.getcwd(), '/Users/swat/dev/compute/www/upload/tests')
testDir = os.path.join(os.getcwd(), '../www/upload/tests')
dbPath = os.path.join(testDir, 'out/uploadDb.db')
uploadPath = os.path.join(testDir, 'in/featureSpace')
appCtxDict = {
    'adminEmail': 'hexmap@ucsc.edu',
    'dev': 1,
    'uploadDbPath': dbPath,
    'uploadPath': uploadPath,
}
appCtx = Context(appCtxDict)
dbData = [
    ['simpleMapName', '2018-09-11', None, 'TBD', 'FULLmatrix.tab', 'FULLmatrix.tab', 5700, 'Success'],
    ['simpleMapName', '2018-09-11', None, 'TBD', 'FULLmatrix2.tab', 'FULLmatrix2.tab', 3364, 'Success'],
    ['groupName', '2018-09-11', None, 'TBD', 'mapName/fullMatrix.tab', 'mapName/fullMatrix.tab', 6475, 'Success'],
    ['groupName', '2018-09-11', None, 'TBD', 'mapName/fullMatrix2.tab', 'mapName/fullMatrix2.tab', 4141, 'Success'],
    ['user_ucsc.edu', '2018-09-11', 'user@ucsc.edu', 'TBD', 'full_matrix_2.tab', 'full_matrix_2.tab', 4922, 'Success'],
    ['user_ucsc.edu', '2018-09-11', 'user@ucsc.edu', 'TBD', 'full_matrix.tab', 'full_matrix.tab', 2583, 'Success']
]

class Test_uploadInit(unittest.TestCase):


    def setUp(self):
        try:
            os.remove(dbPath)
        except:
            pass
        self.db = UploadDb(dbPath)


    def test_getEmail(s):
        r = uploadInit._getEmail('user_ucsc.edu')
        s.assertEqual('user@ucsc.edu', r)


    def test_getEmail_bad(s):
        r = uploadInit._getEmail('__ucsc.edu')
        s.assertEqual('@_ucsc.edu', r)


    def test_getEmail_none(s):
        r = uploadInit._getEmail('a.b.c')
        s.assertEqual(None, r)


    def test_getFileData(s):
        r = uploadInit._getFileData(
            'simpleMapName', 'FULLmatrix.tab', uploadPath, dbPath)
        #print 'r:', r
        s.assertEqual('simpleMapName', r[s.db.authGroupI-1])
        s.assertEqual('2018-09-11', r[s.db.dateI-1])
        s.assertEqual(None, r[s.db.emailI-1])
        s.assertEqual(s.db.tbd, r[s.db.formatI-1])
        s.assertEqual('FULLmatrix.tab', r[s.db.nameI-1])
        s.assertEqual('FULLmatrix.tab', r[s.db.safeNameI-1])
        s.assertEqual(5700, r[s.db.sizeI-1])
        s.assertEqual(s.db.success, r[s.db.statusI-1])


    def test_getFileData_withMinor(s):
        r = uploadInit._getFileData(
            'groupName', 'fullMatrix.tab', uploadPath, dbPath, 'mapName')
        #print 'r:', r
        s.assertEqual('groupName', r[s.db.authGroupI-1])
        s.assertEqual('2018-09-11', r[s.db.dateI-1])
        s.assertEqual(None, r[s.db.emailI-1])
        s.assertEqual(s.db.tbd, r[s.db.formatI-1])
        s.assertEqual('mapName/fullMatrix.tab', r[s.db.nameI-1])
        s.assertEqual('mapName/fullMatrix.tab', r[s.db.safeNameI-1])
        s.assertEqual(6475, r[s.db.sizeI-1])
        s.assertEqual(s.db.success, r[s.db.statusI-1])


    def test_getFileData_withEmail(s):
        r = uploadInit._getFileData(
            'user_ucsc.edu', 'full_matrix.tab', uploadPath, dbPath)
        #print 'r:', r
        s.assertEqual('user_ucsc.edu', r[s.db.authGroupI-1])
        s.assertEqual('2018-09-11', r[s.db.dateI-1])
        s.assertEqual('user@ucsc.edu', r[s.db.emailI-1])
        s.assertEqual(s.db.tbd, r[s.db.formatI-1])
        s.assertEqual('full_matrix.tab', r[s.db.nameI-1])
        s.assertEqual('full_matrix.tab', r[s.db.safeNameI-1])
        s.assertEqual(2583, r[s.db.sizeI-1])
        s.assertEqual(s.db.success, r[s.db.statusI-1])


    def test__getAllData(s):
        r = uploadInit._getAllData(uploadPath, dbPath)
        #print 'r:', r
        s.assertEqual(6, len(r))
        for row in r:
            if row[s.db.authGroupI-1] == 'simpleMapName':
                if row[s.db.nameI-1] == 'FULLmatrix.tab':
                    s.assertEqual('2018-09-11', row[s.db.dateI-1])
                    s.assertEqual(None, row[s.db.emailI-1])
                    s.assertEqual(s.db.tbd, row[s.db.formatI-1])
                    s.assertEqual('FULLmatrix.tab', row[s.db.safeNameI-1])
                    s.assertEqual(5700, row[s.db.sizeI-1])
                    s.assertEqual(s.db.success, row[s.db.statusI-1])
                else:
                    s.assertEqual('2018-09-11', row[s.db.dateI-1])
                    s.assertEqual(None, row[s.db.emailI-1])
                    s.assertEqual(s.db.tbd, row[s.db.formatI-1])
                    s.assertEqual('FULLmatrix2.tab', row[s.db.safeNameI-1])
                    s.assertEqual('FULLmatrix2.tab', row[s.db.nameI-1])
                    s.assertEqual(3364, row[s.db.sizeI-1])
                    s.assertEqual(s.db.success, row[s.db.statusI-1])
            if row[s.db.authGroupI-1] == 'user_ucsc.edu':
                if row[s.db.nameI-1] == 'full_matrix.tab':
                    s.assertEqual('2018-09-11', row[s.db.dateI-1])
                    s.assertEqual('user@ucsc.edu', row[s.db.emailI-1])
                    s.assertEqual(s.db.tbd, row[s.db.formatI-1])
                    s.assertEqual('full_matrix.tab', row[s.db.safeNameI-1])
                    s.assertEqual(2583, row[s.db.sizeI-1])
                    s.assertEqual(s.db.success, row[s.db.statusI-1])
                else:
                    s.assertEqual('2018-09-11', row[s.db.dateI-1])
                    s.assertEqual('user@ucsc.edu', row[s.db.emailI-1])
                    s.assertEqual(s.db.tbd, row[s.db.formatI-1])
                    s.assertEqual('full_matrix_2.tab', row[s.db.safeNameI-1])
                    s.assertEqual('full_matrix_2.tab', row[s.db.nameI-1])
                    s.assertEqual(4922, row[s.db.sizeI-1])
                    s.assertEqual(s.db.success, row[s.db.statusI-1])
            if row[s.db.authGroupI-1] == 'groupName':
                if row[s.db.nameI-1] == 'mapName/fullMatrix.tab':
                    s.assertEqual('2018-09-11', row[s.db.dateI-1])
                    s.assertEqual(None, row[s.db.emailI-1])
                    s.assertEqual(s.db.tbd, row[s.db.formatI-1])
                    s.assertEqual('mapName/fullMatrix.tab', row[s.db.safeNameI-1])
                    s.assertEqual(6475, row[s.db.sizeI-1])
                    s.assertEqual(s.db.success, row[s.db.statusI-1])
                else:
                    s.assertEqual('2018-09-11', row[s.db.dateI-1])
                    s.assertEqual(None, row[s.db.emailI-1])
                    s.assertEqual(s.db.tbd, row[s.db.formatI-1])
                    s.assertEqual('mapName/fullMatrix2.tab', row[s.db.safeNameI-1])
                    s.assertEqual('mapName/fullMatrix2.tab', row[s.db.nameI-1])
                    s.assertEqual(4141, row[s.db.sizeI-1])
                    s.assertEqual(s.db.success, row[s.db.statusI-1])


    def test_loadDb(s):

        uploadInit._loadDb(uploadPath, dbPath)
        r = s.db.getAll()
        #print 'test_loadDb:r:', r
        s.assertEqual(6, len(r))
        for row in r:
            if row[s.db.authGroupI-1] == 'simpleMapName':
                if row[s.db.nameI-1] == 'FULLmatrix.tab':
                    s.assertEqual('2018-09-11', row[s.db.dateI-1])
                    s.assertEqual(None, row[s.db.emailI-1])
                    s.assertEqual(s.db.tbd, row[s.db.formatI-1])
                    s.assertEqual('FULLmatrix.tab', row[s.db.safeNameI-1])
                    s.assertEqual(5700, row[s.db.sizeI-1])
                    s.assertEqual(s.db.success, row[s.db.statusI-1])
                else:
                    s.assertEqual('2018-09-11', row[s.db.dateI-1])
                    s.assertEqual(None, row[s.db.emailI-1])
                    s.assertEqual(s.db.tbd, row[s.db.formatI-1])
                    s.assertEqual('FULLmatrix2.tab', row[s.db.safeNameI-1])
                    s.assertEqual('FULLmatrix2.tab', row[s.db.nameI-1])
                    s.assertEqual(3364, row[s.db.sizeI-1])
                    s.assertEqual(s.db.success, row[s.db.statusI-1])
            if row[s.db.authGroupI-1] == 'user_ucsc.edu':
                if row[s.db.nameI-1] == 'full_matrix.tab':
                    s.assertEqual('2018-09-11', row[s.db.dateI-1])
                    s.assertEqual('user@ucsc.edu', row[s.db.emailI-1])
                    s.assertEqual(s.db.tbd, row[s.db.formatI-1])
                    s.assertEqual('full_matrix.tab', row[s.db.safeNameI-1])
                    s.assertEqual(2583, row[s.db.sizeI-1])
                    s.assertEqual(s.db.success, row[s.db.statusI-1])
                else:
                    s.assertEqual('2018-09-11', row[s.db.dateI-1])
                    s.assertEqual('user@ucsc.edu', row[s.db.emailI-1])
                    s.assertEqual(s.db.tbd, row[s.db.formatI-1])
                    s.assertEqual('full_matrix_2.tab', row[s.db.safeNameI-1])
                    s.assertEqual('full_matrix_2.tab', row[s.db.nameI-1])
                    s.assertEqual(4922, row[s.db.sizeI-1])
                    s.assertEqual(s.db.success, row[s.db.statusI-1])
            if row[s.db.authGroupI-1] == 'groupName':
                if row[s.db.nameI-1] == 'mapName/fullMatrix.tab':
                    s.assertEqual('2018-09-11', row[s.db.dateI-1])
                    s.assertEqual(None, row[s.db.emailI-1])
                    s.assertEqual(s.db.tbd, row[s.db.formatI-1])
                    s.assertEqual('mapName/fullMatrix.tab', row[s.db.safeNameI-1])
                    s.assertEqual(6475, row[s.db.sizeI-1])
                    s.assertEqual(s.db.success, row[s.db.statusI-1])
                else:
                    s.assertEqual('2018-09-11', row[s.db.dateI-1])
                    s.assertEqual(None, row[s.db.emailI-1])
                    s.assertEqual(s.db.tbd, row[s.db.formatI-1])
                    s.assertEqual('mapName/fullMatrix2.tab', row[s.db.safeNameI-1])
                    s.assertEqual('mapName/fullMatrix2.tab', row[s.db.nameI-1])
                    s.assertEqual(4141, row[s.db.sizeI-1])
                    s.assertEqual(s.db.success, row[s.db.statusI-1])


    def test_compareActualFileToDb(s):
        actual = ('user_ucsc.edu', '2018-09-11', 'user@ucsc.edu', 'TBD', 'full_matrix_2.tab', 'full_matrix_2.tab', 4922, 'Success')
        db = (1, 'user_ucsc.edu', '2018-09-11', 'user@ucsc.edu', 'TBD', 'full_matrix_2.tab', 'full_matrix_2.tab', 4922, 'Success')
        r = uploadInit._compareActualFileToDb (actual, db, s.db)
        #for row in r:
        #    print row
        s.assertEqual(0, len(r))


    def test_compareActualFileToDb_oneDifferent(s):
        actual = ('user_ucsc.edu', '2018-09-11', 'user@ucsc.edu', 'TBD', 'full_matrix_2.tab', 'full_matrix_2.tab', 4922, 'Success')
        db = (1, 'user_ucsc.edu', '2018-10-11', 'user@ucsc.edu', 'TBD', 'full_matrix_2.tab', 'full_matrix_2.tab', 4922, 'Success')
        r = uploadInit._compareActualFileToDb (actual, db, s.db)
        #for row in r:
        #    print row
        s.assertEqual(2, len(r))
        s.assertEqual('user_ucsc.edu/full_matrix_2.tab: prop: actual, db:', r[0])
        s.assertEqual('  date: 2018-09-11, 2018-10-11', r[1])


    def test_compareActualFileToDb_allDifferent(s):
        actual = ('user_ucsc.edu', '2018-09-11', 'user@ucsc.edu', 'TBD', 'full_matrix_2.tab', 'full_matrix_2.tab', 4922, 'Success')
        db = (1, 'user_ucsc.edu', '2018-10-11', 'jack@ucsc.edu', 'tbd', 'full_2.tab', 'full_matrix_2.tab', 3000, 'Error')
        r = uploadInit._compareActualFileToDb (actual, db, s.db)
        #for row in r:
        #    print row
        s.assertEqual(7, len(r))
        s.assertEqual('user_ucsc.edu/full_matrix_2.tab: prop: actual, db:', r[0])
        s.assertEqual('  date: 2018-09-11, 2018-10-11', r[1])
        s.assertEqual('  email: user@ucsc.edu, jack@ucsc.edu', r[2])
        s.assertEqual('  format: TBD, tbd', r[3])
        s.assertEqual('  name: full_matrix_2.tab, full_2.tab', r[4])
        s.assertEqual('  size: 4922, 3000', r[5])
        s.assertEqual('  status: Success, Error', r[6])


    def test_compareAllActualToDb(s):
        actual = [
            ('user_ucsc.edu', '2018-09-11', 'user@ucsc.edu', 'TBD', 'full_matrix_2.tab', 'full_matrix_2.tab', 4922, 'Success'),
            ('jack_ucsc.edu', '2018-10-11', 'jack@ucsc.edu', 'tbd', 'full_2.tab', 'full_matrix_2.tab', 3000, 'Success')
        ]
        db = [
            (1, 'user_ucsc.edu', '2018-09-11', 'user@ucsc.edu', 'TBD', 'full_matrix_2.tab', 'full_matrix_2.tab', 4922, 'Success'),
            (1, 'jack_ucsc.edu', '2018-10-11', 'jack@ucsc.edu', 'tbd', 'full_2.tab', 'full_matrix_2.tab', 3000, 'Success')
        ]
        r = uploadInit._compareAllActualToDb (actual, db, s.db)
        #for row in r:
        #    print row
        s.assertEqual(0, len(r))


    def test_compareAllActualToDb_oneDifferent(s):
        actual = [
            ('user_ucsc.edu', '2018-12-11', 'user@ucsc.edu', 'TBD', 'full_matrix_2.tab', 'full_matrix_2.tab', 4922, 'Success'),
            ('jack_ucsc.edu', '2018-10-11', 'jack@ucsc.edu', 'tbd', 'full_2.tab', 'full_matrix_2.tab', 3000, 'Success')
        ]
        db = [
            (1, 'user_ucsc.edu', '2018-09-11', 'user@ucsc.edu', 'TBD', 'full_matrix_2.tab', 'full_matrix_2.tab', 4922, 'Success'),
            (1, 'jack_ucsc.edu', '2018-10-11', 'jack@ucsc.edu', 'tbd', 'full_2.tab', 'full_matrix_2.tab', 3000, 'Success')
        ]
        r = uploadInit._compareAllActualToDb (actual, db, s.db)
        #for row in r:
        #    print row
        s.assertEqual(2, len(r))
        s.assertEqual('user_ucsc.edu/full_matrix_2.tab: prop: actual, db:', r[0])
        s.assertEqual('  date: 2018-12-11, 2018-09-11', r[1])


    def test_compareAllActualToDb_twoDifferent(s):
        actual = [
            ('user_ucsc.edu', '2018-12-11', 'user@ucsc.edu', 'TBD', 'full_matrix_2.tab', 'full_matrix_2.tab', 4922, 'Success'),
            ('jack_ucsc.edu', '2018-12-11', 'jack@ucsc.edu', 'tbd', 'full_2.tab', 'full_matrix_2.tab', 3000, 'Success')
        ]
        db = [
            (1, 'user_ucsc.edu', '2018-09-11', 'user@ucsc.edu', 'TBD', 'full_matrix_2.tab', 'full_matrix_2.tab', 4922, 'Success'),
            (1, 'jack_ucsc.edu', '2018-10-11', 'jack@ucsc.edu', 'tbd', 'full_2.tab', 'full_matrix_2.tab', 3000, 'Success')
        ]
        r = uploadInit._compareAllActualToDb (actual, db, s.db)
        #for row in r:
        #    print row
        #print 'len(r):', len(r)
        s.assertEqual(4, len(r))
        s.assertEqual('user_ucsc.edu/full_matrix_2.tab: prop: actual, db:', r[0])
        s.assertEqual('  date: 2018-12-11, 2018-09-11', r[1])
        s.assertEqual('jack_ucsc.edu/full_matrix_2.tab: prop: actual, db:', r[2])
        s.assertEqual('  date: 2018-12-11, 2018-10-11', r[3])


    def test_findDbEntriesWithoutActualFiles(s):
        actual = [
            ('jack_ucsc.edu', '2018-10-11', 'jack@ucsc.edu', 'tbd', 'full_2.tab', 'full_matrix_2.tab', 3000, 'Success'),
            ('user_ucsc.edu', '2018-09-11', 'user@ucsc.edu', 'TBD', 'full_matrix_2.tab', 'full_matrix_2.tab', 4922, 'Success'),
        ]
        db = [
            (1, 'user_ucsc.edu', '2018-09-11', 'user@ucsc.edu', 'TBD', 'full_matrix_2.tab', 'full_matrix_2.tab', 4922, 'Success'),
            (2, 'jack_ucsc.edu', '2018-10-11', 'jack@ucsc.edu', 'tbd', 'full_2.tab', 'full_matrix_2.tab', 3000, 'Success')
        ]
        r = uploadInit._dbEntriesWithoutFiles(actual, db, s.db)
        #for row in r:
        #    print row
        #print 'len(r):', len(r)
        s.assertEqual(0, len(r))


    def test_findDbEntriesWithoutActualFilesOne(s):
        actual = [
            ('jack_ucsc.edu', '2018-10-11', 'jack@ucsc.edu', 'tbd', 'full_2.tab', 'full_matrix_2.tab', 3000, 'Success')
        ]
        db = [
            (1, 'user_ucsc.edu', '2018-09-11', 'user@ucsc.edu', 'TBD', 'full_matrix_2.tab', 'full_matrix_2.tab', 4922, 'Success'),
            (2, 'jack_ucsc.edu', '2018-10-11', 'jack@ucsc.edu', 'tbd', 'full_2.tab', 'full_matrix_2.tab', 3000, 'Success')
        ]
        r = uploadInit._dbEntriesWithoutFiles(actual, db, s.db)
        #for row in r:
        #    print row
        #print 'len(r):', len(r)
        s.assertEqual(1, len(r))
        s.assertEqual('user_ucsc.edu/full_matrix_2.tab: DB entry without actual file', r[0])


    def test_findDbEntriesWithoutActualFilesTwo(s):
        actual = []
        db = [
            (1, 'user_ucsc.edu', '2018-09-11', 'user@ucsc.edu', 'TBD', 'full_matrix_2.tab', 'full_matrix_2.tab', 4922, 'Success'),
            (2, 'jack_ucsc.edu', '2018-10-11', 'jack@ucsc.edu', 'tbd', 'full_2.tab', 'full_matrix_2.tab', 3000, 'Success')
        ]
        r = uploadInit._dbEntriesWithoutFiles(actual, db, s.db)
        #for row in r:
        #    print row
        #print 'len(r):', len(r)
        s.assertEqual(2, len(r))
        s.assertEqual('user_ucsc.edu/full_matrix_2.tab: DB entry without actual file', r[0])
        s.assertEqual('jack_ucsc.edu/full_matrix_2.tab: DB entry without actual file', r[1])


    def test_compareActualAndDb(s):
        s.db.loadInitial(dbData)
        r = uploadInit._compareActualAndDb(uploadPath, dbPath)
        #for row in r:
        #    print row
        #print 'len(r):', len(r)
        s.assertEqual(0, len(r))


    def test_compareActualAndDb_fileWithoutDB(s):
        data = dbData[0:5]
        s.db.loadInitial(data)
        r = uploadInit._compareActualAndDb(uploadPath, dbPath)
        #for row in r:
        #    print row
        #print 'len(r):', len(r)
        s.assertEqual(1, len(r))
        s.assertEqual('user_ucsc.edu/full_matrix.tab: file not in DB', r[0])


    def test_compareActualAndDb_dbWithoutFile(s):
        data = dbData
        data.append(['user_ucsc.edu', '2018-09-11', 'user@ucsc.edu', 'TBD', 'full_Sim.tab', 'full_Sim.tab', 2583, 'Success'])
        s.db.loadInitial(data)
        r = uploadInit._compareActualAndDb(uploadPath, dbPath)
        #for row in r:
        #    print row
        #print 'len(r):', len(r)
        s.assertEqual(1, len(r))
        s.assertEqual('user_ucsc.edu/full_Sim.tab: DB entry without actual file', r[0])
    

if __name__ == '__main__':
    unittest.main()
