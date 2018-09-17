#!/usr/bin/env python2.7

# This tests the upload database functionality.

import os
from datetime import date
import json

import unittest
import testUtil as util
import upload
from uploadDb import UploadDb

testDir = os.path.join(os.getcwd(), '../www/upload/tests')
dbPath = os.path.join(testDir, 'out/uploadDb.db')

email = 'user@ucsc.edu'
authGroup = 'user_ucsc.edu'
name = 'myFeature!Input.tab'
major = 'user_ucsc.edu'
minor = 'minorDir'
size = 808

email1 = 'george@ucsc.edu'
authGroup1 = 'george_ucsc.edu'
name1 = 'george!Input.tab'
major1 = 'george_ucsc.edu'
minor1 = 'minor1Dir'
size1 = 666

email3 = 'user@ucsc.edu'
authGroup3 = 'user_ucsc.edu'
name3 = 'myAttr!Input.tab'
major3 = 'user_ucsc.edu'
minor3 = 'minor3Dir'
size3 = 808

authGroupPub = 'public'
sizePub = 999
namePub = 'public!.tab'
majorPub = 'unitTest'
minorPub = 'layoutBasicExp'

isoToday = date.today().isoformat()


class Test_uploadDb(unittest.TestCase):


    def setUp(self):
        try:
            os.remove(dbPath)
        except:
            pass
        self.db = UploadDb(dbPath)


    def test_add(s):
        r = s.db.addOne(authGroup, name, major, minor, size, email)

        # Verify correct upload ID was returned.
        #print 'r:', r
        s.assertEqual(1, r);
        
        # Verify fields were initialized properly.
        out = s.db._getOne(1)
        #print 'out:', out
        s.assertEqual(1, out[s.db.idI])
        s.assertEqual(isoToday, out[s.db.dateI])
        s.assertEqual(email, out[s.db.emailI])
        s.assertEqual('TBD', out[s.db.formatI])
        s.assertEqual('user_ucsc.edu', out[s.db.authGroupI])
        s.assertEqual('myFeature_Input.tab', out[s.db.nameI])
        s.assertEqual(major, out[s.db.majorI])
        s.assertEqual(minor, out[s.db.minorI])
        s.assertEqual(size, out[s.db.sizeI])
        s.assertEqual(s.db.uploading, out[s.db.statusI])
    
    
    def test_addPublic(s):
        r = s.db.addOne(authGroupPub, namePub, majorPub, minorPub, sizePub)

        # Verify correct upload ID was returned.
        #print 'r:', r
        s.assertEqual(1, r);

        # Verify fields were initialized properly.
        out = s.db._getOne(1)
        #print 'out:', out
        s.assertEqual(1, out[s.db.idI])
        s.assertEqual(isoToday, out[s.db.dateI])
        s.assertEqual(None, out[s.db.emailI])
        s.assertEqual(s.db.tbd, out[s.db.formatI])
        s.assertEqual(authGroupPub, out[s.db.authGroupI])
        s.assertEqual('public_.tab', out[s.db.nameI])
        s.assertEqual(majorPub, out[s.db.majorI])
        s.assertEqual(minorPub, out[s.db.minorI])
        s.assertEqual(sizePub, out[s.db.sizeI])
        s.assertEqual(s.db.uploading, out[s.db.statusI])
    
    
    def test_getOne(s):
        r = s.db.addOne(authGroup, name, major, minor, size, email)
        row = s.db._getOne(1)
        s.assertEqual(1, row[s.db.idI])
    
    
    def test_getOneWithNone(s):
        row = s.db._getOne(1)
        s.assertEqual(None, row)
    
    
    def test_delete(s):
        r = s.db.addOne(authGroup, name, major, minor, size, email)
        #print 'r:', r
        s.db.delete(r)
        row = s.db._getOne(1)
        s.assertEqual(None, row)
    
    
    def test_getAll(s):
        s.db.addOne(authGroup, name, major, minor, size, email)
        s.db.addOne(authGroupPub, namePub, majorPub, minorPub, sizePub)
        s.db.addOne(authGroup1, name1, major1, minor1, size1, email1)
        r = s.db.getAll()
        s.assertEqual(3, len(r))
    
    
    def test_getGroup(s):
        s.db.addOne(authGroup, name, major, minor, size, email)
        s.db.addOne(authGroupPub, namePub, majorPub, minorPub, sizePub)
        s.db.addOne(authGroup3, name3, major3, minor3, size3, email3)
        r = s.db.getGroupFiles(authGroup)
        #print 'r:', r
        s.assertEqual(2, len(r))


    def test_getPublic(s):
        s.db.addOne(authGroup, name, major, minor, size, email)
        s.db.addOne(authGroupPub, namePub, majorPub, minorPub, sizePub)
        s.db.addOne(authGroup3, name3, major3, minor3, size3, email3)
        r = s.db.getPublicFiles()
        #print 'r:', r
        s.assertEqual(1, len(r))


    def test_updateFormat(s):
        s.db.addOne(authGroup, name, major, minor, size, email)
        r = s.db.updateFormat(1, s.db.featureMatrix)
        #print 'r:', r
        row = s.db._getOne(1)
        #print 'row:', row
        s.assertEqual(s.db.featureMatrix, row[s.db.formatI]);


    def test_updateStatus(s):
        s.db.addOne(authGroup, name, major, minor, size, email)
        r = s.db.updateStatus(1, s.db.error)
        #print 'r:', r
        row = s.db._getOne(1)
        #print 'row:', row
        s.assertEqual(s.db.error, row[s.db.statusI]);

        
    def test_hasData(s):
        r = s.db.addOne(authGroup, name, major, minor, size, email)
        hasData = s.db.hasData()
        s.assertEqual(True, hasData)
    

    def test_loadInitial(s):
        data = [
            ['public', '2018-09-11', None, 'TBD', 'fullMatrix.tab', 'groupName', 'mapName', 6475, 'Success'],
            ['public', '2018-09-11', None, 'TBD', 'fullMatrix2.tab', 'groupName', 'mapName', 4141, 'Success'],
            ['public', '2018-09-11', None, 'TBD', 'FULLmatrix.tab', 'simpleMapName', None, 5700, 'Success'],
            ['public', '2018-09-11', None, 'TBD', 'FULLmatrix2.tab', 'simpleMapName', None, 3364, 'Success'],
            ['user_ucsc.edu', '2018-09-11', 'user@ucsc.edu', 'TBD', 'full_matrix_2.tab', 'user_ucsc.edu', None, 4922, 'Success'],
            ['user_ucsc.edu', '2018-09-11', 'user@ucsc.edu', 'TBD', 'full_matrix.tab', 'user_ucsc.edu', None, 2583, 'Success']
        ]

        s.db.loadInitial(data)
        r = s.db.getAll()
        #print 'test_loadInitial:r:', r
        for row in r:
            if row[s.db.majorI-1] == 'groupName':
                if row[s.db.nameI-1] == 'fullMatrix.tab':
                    s.assertEqual('public', row[s.db.authGroupI-1])
                    s.assertEqual('2018-09-11', row[s.db.dateI-1])
                    s.assertEqual(None, row[s.db.emailI-1])
                    s.assertEqual(s.db.tbd, row[s.db.formatI-1])
                    s.assertEqual('mapName', row[s.db.minorI-1])
                    s.assertEqual(6475, row[s.db.sizeI-1])
                    s.assertEqual(s.db.success, row[s.db.statusI-1])
                else:
                    s.assertEqual('public', row[s.db.authGroupI-1])
                    s.assertEqual('2018-09-11', row[s.db.dateI-1])
                    s.assertEqual(None, row[s.db.emailI-1])
                    s.assertEqual(s.db.tbd, row[s.db.formatI-1])
                    s.assertEqual('mapName', row[s.db.minorI-1])
                    s.assertEqual(4141, row[s.db.sizeI-1])
                    s.assertEqual(s.db.success, row[s.db.statusI-1])
            if row[s.db.majorI-1] == 'simpleMapName':
                if row[s.db.nameI-1] == 'FULLmatrix.tab':
                    s.assertEqual('public', row[s.db.authGroupI-1])
                    s.assertEqual('2018-09-11', row[s.db.dateI-1])
                    s.assertEqual(None, row[s.db.emailI-1])
                    s.assertEqual(s.db.tbd, row[s.db.formatI-1])
                    s.assertEqual(None, row[s.db.minorI-1])
                    s.assertEqual(5700, row[s.db.sizeI-1])
                    s.assertEqual(s.db.success, row[s.db.statusI-1])
                else:
                    s.assertEqual('public', row[s.db.authGroupI-1])
                    s.assertEqual('2018-09-11', row[s.db.dateI-1])
                    s.assertEqual(None, row[s.db.emailI-1])
                    s.assertEqual(s.db.tbd, row[s.db.formatI-1])
                    s.assertEqual(None, row[s.db.minorI-1])
                    s.assertEqual(3364, row[s.db.sizeI-1])
                    s.assertEqual(s.db.success, row[s.db.statusI-1])
            if row[s.db.majorI-1] == 'user_ucsc.edu':
                if row[s.db.nameI-1] == 'full_matrix.tab':
                    s.assertEqual('user_ucsc.edu', row[s.db.authGroupI-1])
                    s.assertEqual('2018-09-11', row[s.db.dateI-1])
                    s.assertEqual('user@ucsc.edu', row[s.db.emailI-1])
                    s.assertEqual(s.db.tbd, row[s.db.formatI-1])
                    s.assertEqual('user_ucsc.edu', row[s.db.majorI-1])
                    s.assertEqual(None, row[s.db.minorI-1])
                    s.assertEqual(2583, row[s.db.sizeI-1])
                    s.assertEqual(s.db.success, row[s.db.statusI-1])
                else:
                    s.assertEqual('user_ucsc.edu', row[s.db.authGroupI-1])
                    s.assertEqual('2018-09-11', row[s.db.dateI-1])
                    s.assertEqual('user@ucsc.edu', row[s.db.emailI-1])
                    s.assertEqual(s.db.tbd, row[s.db.formatI-1])
                    s.assertEqual('user_ucsc.edu', row[s.db.majorI-1])
                    s.assertEqual(None, row[s.db.minorI-1])
                    s.assertEqual(4922, row[s.db.sizeI-1])
                    s.assertEqual(s.db.success, row[s.db.statusI-1])

    
if __name__ == '__main__':
    unittest.main()
