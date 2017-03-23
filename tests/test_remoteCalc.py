#!/usr/bin/env python2.7

# This tests the remote calc server via meteor, although it is really on the same server

import sys, os, glob, subprocess, json, tempfile, pprint, requests
from os import path
import string
import unittest
import testUtil as util

# There are two servers involved in these tests:
# - main server
mainUrlPrefix = "localhost:5555"
# - calc server
calcUrlPrefix = "localhost:4444"

testDir = os.getcwd()
inDir = path.join(testDir, 'in/layout/')
outDir = path.join(testDir, 'out/remoteCalc/')

class Test_remoteCalc(unittest.TestCase):

    # The main server needs defined in settings.json:
    # IS_MAIN_SERVER and NOT IS_CALC_SERVER.
    
    # The calc server needs defined in settings.json:
    # IS_CALC_SERVER, MAIN_MONGO_URL and NOT IS_MAIN_SERVER.

    viewServer = os.environ['VIEWER_URL']

    def cleanDataOut(s, dataOut):
        data = dataOut
    
        # if this is an error message ...
        if dataOut[0] != '{':
            data = dataOut.replace('\n', '')
            
        return data
        
    def findStatusCode(s, verbose):
        i = verbose.find('< HTTP/1.1')
        return verbose[i+11:i+14]
        
    def checkLog(s, filename):
        with open(filename, 'r') as f:
            log = f.read()
        if log.find('Visualization generation complete!') > -1:
            return True
        else:
            return False
        
    def doCurl(s, opts, urlSuffix):
        o, outfile = tempfile.mkstemp()
        e, errfile = tempfile.mkstemp()
        #print 's.viewServer',  s.viewServer
        url = s.viewServer + urlSuffix
        #print "url", url
        with open(outfile, 'w') as o:
            e = open(errfile, 'w')
            curl = ['curl', '-s', '-k'] + opts + [url]
            #print 'curl:\n', curl, '\n\n'
            subprocess.check_call(curl, stdout=o, stderr=e);
            e.close()
        with open(outfile, 'r') as o:
            e = open(errfile, 'r')
            data = s.cleanDataOut(o.read());
            code = s.findStatusCode(e.read());
            e.close()
        os.remove(outfile)
        os.remove(errfile)
        return {'data': data, 'code': code}

    def test_view_server_connection(s):
        try:
            bResult = requests.post(
                s.viewServer + '/test',
                #cert=(ctx['sslCert'], ctx['sslKey']),
                verify=False,
                headers = { 'Content-type': 'application/json' },
            )
        except:
            s.assertEqual('', 'Unable to connect to view server: ' +
                s.viewServer + '. Is it up?')

    def test_createMap(s):
        data = '[ ' + \
            '"--coordinates", "' + path.join(inDir, "example_features_xy.tab") + '", ' + \
            '"--names", "layout", ' + \
            '"--directory", "' + outDir + '", ' + \
            '"--include-singletons", ' + \
            '"--no_density_stats", ' + \
            '"--no_layout_independent_stats", ' + \
            '"--no_layout_aware_stats" ]'
        curl_opts = ['-d', data, '-H', 'Content-Type:application/json', '-X', 'POST', '-v']
        rc = s.doCurl(curl_opts, '/calc/layout')
        #print 'code, data:', rc['code'], rc['data']
        s.assertTrue(rc['code'] == '200')
    
if __name__ == '__main__':
    unittest.main()
