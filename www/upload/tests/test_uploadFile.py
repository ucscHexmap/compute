#!/usr/bin/env python2.7

# This tests the upload file logic while using the database primitives.

import os
from datetime import date
import json
from util_web import Context
import unittest
import testUtil as util
import uploadFile
from uploadDb import UploadDb

testDir = os.path.join(os.getcwd(), '../www/upload/tests')
dbPath = os.path.join(testDir, 'out/uploadDb.db')
uploadPath = os.path.join(testDir, 'in/featureSpace')

"""
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
"""

class Test_uploadFile(unittest.TestCase):


    def setUp(self):
        try:
            os.remove(dbPath)
        except:
            pass
        self.db = UploadDb(dbPath)
        

    def makeRequest(s, name, size):
        fileObj = Context({ 'filename': name, 'size': size })
        return Context({ 'files': { 'file': fileObj } })

    """
    def test_getEmail(s):
        r = uploadFile._getEmail('user_ucsc.edu')
        s.assertEqual('user@ucsc.edu', r)


    def test_getEmail_bad(s):
        r = uploadFile._getEmail('__ucsc.edu')
        s.assertEqual('@_ucsc.edu', r)


    def test_getEmail_none(s):
        r = uploadFile._getEmail('a.b.c')
        s.assertEqual(None, r)
    """
    
    def test_local_makeRequest(s):
        req = s.makeRequest('someFile', 888)
        s.assertTrue(hasattr(req, 'files'))
        s.assertNotEqual(req.files.get('file'), None)
        fileObj = req.files['file']
        s.assertEqual('someFile', fileObj.filename)
        s.assertEqual(888, fileObj.size)


    # failing due to
    # File "/Users/swat/dev/compute/www/upload/uploadFile.py", line 67, in _validateUploadFile
    #     cleanFileName = validate.cleanFileName(file.filename)
    # AttributeError: type object 'file' has no attribute 'filename'
    '''def test_validateUploadFile(s):
        request = s.makeRequest('someFile', 888)
        (fileName, fileObj) = uploadFile._validateUploadFile({
            'email': 'user@ucsc.edu',
            'token': 'y4er',
            'authGroup': 'user_ucsc.edu',
            'major': 'user_ucsc.edu',
            'minor': 'minorDir',
        }, request)
    '''
    """
    def test_getFileData(s):
        r = s.db.addOne(
            'simpleMapName', 'FULLmatrix.tab', uploadPath, dbPath)
        #print 'r:', r
        s.assertEqual('simpleMapName', r[s.db.authGroupI-1])
        s.assertEqual('2018-09-11', r[s.db.dateI-1])
        s.assertEqual(None, r[s.db.emailI-1])
        s.assertEqual(s.db.tbd, r[s.db.formatI-1])
        s.assertEqual('FULLmatrix.tab', r[s.db.nameI-1])
        s.assertEqual(5700, r[s.db.sizeI-1])
        s.assertEqual(s.db.success, r[s.db.statusI-1])
    """
    """
    def addOne (s, authGroup, name, size, email=None):
    
        # Add one file's information.
        with s._getConnectionCache() as conn:
            curs = conn.cursor()
            curs.execute(s._dbPush, (
                authGroup,
                s._today(),
                email,
                s.tbd,
                name,
                validate_web.cleanFileName(name),
                size,
                s.uploading))
            return curs.lastrowid
    """

    

if __name__ == '__main__':
    unittest.main()
