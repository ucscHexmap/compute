#!/usr/bin/env python2.7

# This tests the upload database functionality.

import os
import datetime
import json

import unittest
import testUtil as util
import upload
from uploadDb import UploadDb

testDir = os.getcwd()
dbPath = os.path.join(os.getcwd() , 'out/uploadDb.db') # database file path

email = 'user@ucsc.edu'
authGroup = 'user_ucsc.edu'
name = 'myFeature!Input.tab'
size = 808

email1 = 'george@ucsc.edu'
authGroup1 = 'george_ucsc.edu'
name1 = 'george!Input.tab'
size1 = 666

email2 = 'tran@ucsc.edu'
authGroup2 = 'tran_ucsc.edu'
name2 = 'tran!Input.tab'
size2 = 777

email3 = 'user@ucsc.edu'
authGroup3 = 'user_ucsc.edu'
name3 = 'myAttr!Input.tab'
size3 = 808

authGroupPub = 'public'
sizePub = 999
namePub = 'public!.tab'

isoToday = str(datetime.date.today())


class Test_uploadDb(unittest.TestCase):


    def setUp(self):
        try:
            os.remove(dbPath)
        except:
            pass
        self.db = UploadDb(dbPath)


    def test_add(s):
        r = s.db.addOne(authGroup, name, size, email)

        # Verify correct upload ID was returned.
        #print 'r:', r
        s.assertEqual(1, r);
        
        # Verify fields were initialized properly.
        out = s.db._getOne(1)
        #print 'out:', out
        s.assertEqual(1, out[s.db.idI])
        s.assertEqual('myFeature_Input.tab', out[s.db.baseNameI])
        s.assertEqual(isoToday, out[s.db.dateI])
        s.assertEqual(email, out[s.db.emailI])
        s.assertEqual('TBD', out[s.db.formatI])
        s.assertEqual('user_ucsc.edu', out[s.db.authGroupI])
        s.assertEqual(name, out[s.db.nameI])
        s.assertEqual(size, out[s.db.sizeI])
        s.assertEqual(s.db.uploading, out[s.db.statusI])
    

    def test_addPublic(s):
        r = s.db.addOne(authGroupPub, namePub, sizePub)

        # Verify correct upload ID was returned.
        #print 'r:', r
        s.assertEqual(1, r);

        # Verify fields were initialized properly.
        out = s.db._getOne(1)
        #print 'out:', out
        s.assertEqual(1, out[s.db.idI])
        s.assertEqual('public_.tab', out[s.db.baseNameI])
        s.assertEqual(isoToday, out[s.db.dateI])
        s.assertEqual(None, out[s.db.emailI])
        s.assertEqual('TBD', out[s.db.formatI])
        s.assertEqual(authGroupPub, out[s.db.authGroupI])
        s.assertEqual(namePub, out[s.db.nameI])
        s.assertEqual(sizePub, out[s.db.sizeI])
        s.assertEqual(s.db.uploading, out[s.db.statusI])
    

    def test_getOne(s):
        r = s.db.addOne(authGroup, name, size, email)
        row = s.db._getOne(1)
        s.assertEqual(1, row[s.db.idI])
    
    
    def test_getOneWithNone(s):
        row = s.db._getOne(1)
        s.assertEqual(None, row)
    
    
    def test_delete(s):
        r = s.db.addOne(authGroup, name, size, email)
        #print 'r:', r
        s.db.delete(r)
        row = s.db._getOne(1)
        s.assertEqual(None, row)
    
    
    def test_getAll(s):
        s.db.addOne(authGroup, name, size, email)
        s.db.addOne(authGroupPub, namePub, sizePub)
        s.db.addOne(authGroup1, name1, size1, email1)
        r = s.db.getAll()
        s.assertEqual(3, len(r))
    
    
    def test_getGroup(s):
        s.db.addOne(authGroup, name, size, email)
        s.db.addOne(authGroupPub, namePub, sizePub)
        s.db.addOne(authGroup3, name3, size3, email3)
        r = s.db.getGroupFiles(authGroup)
        #print 'r:', r
        s.assertEqual(2, len(r))


    def test_getPublic(s):
        s.db.addOne(authGroup, name, size, email)
        s.db.addOne(authGroupPub, namePub, sizePub)
        s.db.addOne(authGroup3, name3, size3, email3)
        r = s.db.getPublicFiles()
        #print 'r:', r
        s.assertEqual(1, len(r))


    def test_updateFormat(s):
        s.db.addOne(authGroup, name, size, email)
        r = s.db.updateFormat(1, s.db.featureMatrix)
        #print 'r:', r
        row = s.db._getOne(1)
        #print 'row:', row
        s.assertEqual(s.db.featureMatrix, row[s.db.formatI]);


    def test_updateStatus(s):
        s.db.addOne(authGroup, name, size, email)
        r = s.db.updateStatus(1, s.db.error)
        #print 'r:', r
        row = s.db._getOne(1)
        #print 'row:', row
        s.assertEqual(s.db.error, row[s.db.statusI]);

        
    def test_hasData(s):
        r = s.db.addOne(authGroup, name, size, email)
        hasData = s.db.hasData()
        s.assertEqual(True, hasData)


if __name__ == '__main__':
    unittest.main()
