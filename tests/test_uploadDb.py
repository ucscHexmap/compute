#!/usr/bin/env python2.7

# This tests the upload DB functionality without going through HTTP.

import os
import datetime
import json

import unittest
import testUtil as util
import upload
from uploadDb import UploadDb
#import uploadDb as db
from util_web import Context

# TODO create a dir: out
testDir = os.getcwd()
dbPath = os.path.join(os.getcwd() , 'out/uploadDb.db') # database file name
uploadPath = os.path.join(os.getcwd() , 'out/upload') # upload dir path
os.mkdir(uploadPath)


'''
# Job context
ctx2 = 'ctx2'
ctx3 = 'ctx3'

uploadStatusUrl = 'http://127.0.0.1:5000/uploadStatus/uploadId/'

appCtxDict = {
    'dev': int(os.environ.get('DEV', 0)),
    'uploadDbPath': dbPath,
    #'uploadStatusUrl': uploadStatusUrl,
    #'unitTest': True,
    #'adminEmail': 'admin@x.y',
}
appCtx = Context(appCtxDict)
appCtxUnicode = json.loads(json.dumps(appCtxDict))

ctx1NoAppUnicode = json.loads(json.dumps({'email': 'user1', 'prop1': 1}))
ctxdict = {'app': appCtx}
ctx1 = Context(ctxdict)
ctx1.prop1 = 1
ctx2 = Context(ctxdict)
ctx2.prop2 = 2
ctx3 = Context(ctxdict)
ctx3.prop3 = 3

# Tasks to execute as stored in the db.
task1 = '{"ctx":{"app":{"adminEmail":"admin@x.y","dev":' + str(appCtx.dev) + ',"uploadDbPath":"' + dbPath + '","uploadStatusUrl":"' + uploadStatusUrl + '","unitTest":true},"email":"user1","prop1":1},"operation":"uploadTestHelper","parms":{"parms1":"parms1"}}'
task2 = '{"ctx":{"app":{"adminEmail":"admin@x.y","dev":1,"uploadDbPath":"' + dbPath + '","uploadStatusUrl":"' + uploadStatusUrl + '","unitTest":true},"prop2":2},"operation":"operation2","parms":"parms2"}'
task3 = '{"ctx":{"app":{"adminEmail":"admin@x.y","dev":1,"uploadDbPath":"' + dbPath + '","uploadStatusUrl":"' + uploadStatusUrl + '","unitTest":true},"prop3":3},"operation":"operation3","parms":"parms3"}'

# Usernames
user1 = 'user1'
user2 = 'user2'
user3 = 'user3'

# Results
result1 = {u'myResult': u'result1'}
result2 = 'result2'
result3 = 'result3'
result1unicode = json.loads(json.dumps(result1))

# Error message
errorMsg1 = {"error": "some error"}
errorMsg1trace = {"error": "some error", "stackTrace": "some stackTrace"}
errorMsg2 = 'errorMsg2'
errorMsg2 = 'errorMsg3'

# Test operation
operation1 = 'uploadTestHelper'
operation2 = 'operation2'
operation3 = 'operation3'

# Parameters to a calc operation
parms1 = {"parms1":"parms1"}
parms2 = 'parms2'
parms3 = 'parms3'

'''
isoToday = str(datetime.date.today())

class Test_upload(unittest.TestCase):

    print 'test: dbPath:', dbPath
    def setUp(self):
        try:
            os.remove(dbPath)
        except:
            pass
        self.db = UploadDb(dbPath)

    def test_add(s):
        email = 'user@ucsc.edu'
        group = 'user_ucsc.edu'
        name = 'myFeature-Input.tab'
        size = 808
        r = upload.add(email, group, name, size, uploadPath, s.db)

        # Verify correct upload ID was returned.
        s.assertEqual(1, r['id']);

        # Verify fields were initialized properly.
        out = s.db._getOne(1)
        #print 'out:', out
        s.assertEqual(1, out[s.db.idI])
        s.assertEqual('myFeature_Input.tab', out[s.db.baseNameI])
        s.assertEqual(isoToday(), out[s.db.dateI])
        s.assertEqual('user@ucsc.edu', out[s.db.emailI])
        s.assertEqual('TBD', out[s.db.formatI])
        s.assertEqual('user_ucsc.edu', out[s.db.groupI])
        s.assertEqual('myFeature-Input.tab', out[s.db.nameI])
        s.assertEqual(808, out[s.db.sizeI])
        s.assertEqual(s.db.uploadingSt, out[s.db.statusI])
    '''
    def test_getOne(s):
        upload.add(user1, operation1, parms1, ctx1);
        aJob = s.db._getOne(1)
        s.assertEqual(1, aJob[s.db.idI])
    
    def test_getOneWithNone(s):
        aJob = s.db._getOne(1)
        s.assertEqual(None, aJob)
    
    def test__getStatus(s):
    
        # Test the db getStatus()
        upload.add(user1, operation1, parms1, ctx1);
        r = s.db.getStatus(1)
        s.assertEqual(s.db.inUploadDbSt, r['status']);
        s.assertFalse('result' in r)

    def test__getStatusBadJobId(s):
    
        # Test the db getStatus() for unknown upload ID
        r = s.db.getStatus(1)
        s.assertEqual(None, r);
    
    def test_getStatusInUploadDb(s):

        # Test the upload getStatus()
        upload.add(user1, operation1, parms1, ctx1);
        r = upload.getStatus(1, dbPath)
        s.assertEqual(s.db.inUploadDbSt, r['status']);
        s.assertFalse('result' in r)

    def test_getStatusRunning(s):
        upload.add(user1, operation1, parms1, ctx1);
        s.db.setResult(1, s.db.runningSt, None, ctx1, operation1)
        r = upload.getStatus(1, dbPath)
        #print 'r:', r
        s.assertEqual(s.db.runningSt, r['status']);
        s.assertFalse('result' in r)

    def test_getStatusSuccess(s):
        upload.add(user1, operation1, parms1, ctx1);
        s.db.setResult(1, s.db.successSt, result1, ctx1, operation1)
        r = upload.getStatus(1, dbPath)
        #print 'r:', r
        s.assertEqual(s.db.successSt, r['status']);
        #s.assertEqual(json.dumps('result1'), r['result']);
        s.assertEqual(result1, r['result']);

    def test_getStatusError(s):
        upload.add(user1, operation1, parms1, ctx1);
        s.db.setResult(1, s.db.errorSt, errorMsg1, ctx1, operation1)
        r = upload.getStatus(1, dbPath)
        s.assertEqual(s.db.errorSt, r['status']);
        s.assertEqual(errorMsg1, r['result']);

    def test_getStatusErrorWithTrace(s):
        upload.add(user1, operation1, parms1, ctx1);
        s.db.setResult(1, s.db.errorSt, errorMsg1trace, ctx1, operation1)
        r = upload.getStatus(1, dbPath)
        s.assertEqual(s.db.errorSt, r['status']);
        s.assertEqual(errorMsg1trace, r['result']);
    '''
if __name__ == '__main__':
    unittest.main()
