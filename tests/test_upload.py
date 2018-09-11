#!/usr/bin/env python2.7

# This tests the upload logic between routes and the database.

import os
import datetime
import json

import unittest
import testUtil as util
import upload
from uploadDb import UploadDb

testDir = os.getcwd()
dbPath = os.path.join(testDir, 'out/uploadDb.db')
uploadPath = os.path.join(testDir, 'in/dataRoot/featureSpace')

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

#isoToday = str(datetime.date.today())

class Test_upload(unittest.TestCase):


    def setUp(self):
        try:
            os.remove(dbPath)
        except:
            pass
        self.db = UploadDb(dbPath)


    def test_getEmail(s):
        r = upload._getEmail(authGroup)
        s.assertEqual(email, r)

        
if __name__ == '__main__':
    unittest.main()
