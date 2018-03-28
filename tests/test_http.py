#!/usr/bin/env python2.7

# This tests http

import sys, os, glob, subprocess, json, tempfile, pprint
from os import path
import string, requests
import unittest
import testUtil as util

testDir = os.getcwd()
inDir = path.join(testDir, 'in/layout/')
outDir = path.join(testDir, 'out/http/')

class Test_http(unittest.TestCase):

    viewServer = os.environ['VIEWER_URL']

    def test_view_server_connection(s):
        try:
            bResult = requests.post(
                s.viewServer + '/test',
                #cert=(ctx['sslCert'], ctx['sslKey']),
                verify=True,
                headers = { 'Content-type': 'application/json' },
            )
        except:
            s.assertEqual('', 'Unable to connect to view server: ' +
                s.viewServer + '. Is it up?')

    
if __name__ == '__main__':
    unittest.main()
