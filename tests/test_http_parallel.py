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

class Test_http_parallel(unittest.TestCase):

    viewServer = os.environ['VIEWER_URL']

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
        
    def doCurl(s, opts):
        o, outfile = tempfile.mkstemp()
        e, errfile = tempfile.mkstemp()
        url = s.viewServer + "/calc/layout"
        with open(outfile, 'w') as o:
            e = open(errfile, 'w')
            curl = ['curl', '-s', '-k'] + opts + [url]
            #print 'curl:\n', curl, '\n\n'
# curl -s -k -d '{"map": "CKCC/v1", "nodes": {"Sample-2": {"CTD-2588J6.1": "0", "RP11-433M22.1": "0", "CTD-2588J6.2": "0", "CPHL1P": "0", "RP3-415N12.1": "0", "RP11-181G12.4": "0", "RP11-433M22.2": "0", "SSXP10": "0", "RP11-16E12.2": "2.5424", "PSMA2P3": "0", "CTD-2367A17.1": "0", "RP11-181G12.2": "5.9940", "AC007272.3": "0"}, "Sample-1": {"CTD-2588J6.1": "0", "RP11-433M22.1": "0", "CTD-2588J6.2": "0", "CPHL1P": "0", "RP3-415N12.1": "0", "RP11-181G12.4": "0.5264", "RP11-433M22.2": "0", "SSXP10": "0", "RP11-16E12.2": "2.3112", "PSMA2P3": "0", "CTD-2367A17.1": "0", "RP11-181G12.2": "6.3579", "AC007272.3": "0"}}, "layout": "mRNA"}' -H Content-Type:application/json -X POST -v localhost:3333/query/overlayNodes
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

    def test_pythonCallGoodDataLocal(s):
        util.removeOldOutFiles(outDir)
        data = '[ ' + \
            '"--coordinates", "' + path.join(inDir, "coordinates.tab") + '", ' + \
            '"--names", "layout", ' + \
            '"--directory", "' + outDir + '", ' + \
            '"--include-singletons", ' + \
            '"--no_layout_independent_stats", ' + \
            '"--no_layout_aware_stats" ]'
        curl_opts = ['-d', data, '-H', 'Content-Type:application/json', '-X', 'POST', '-v']
        rc = s.doCurl(curl_opts)
        #print 'code, data:', rc['code'], rc['data']
        s.assertTrue(rc['code'] == '200')
    
    def test_createMap_sparse(s):
        util.removeOldOutFiles(outDir)
        data = '[ ' + \
            '"--similarity", "' + path.join(inDir, "similarity.tab") + '", ' + \
            '"--names", "mRNA", ' + \
            '"--scores", "' + path.join(inDir, "attributes.tab") + '", ' + \
            '"--directory", "' + outDir + '", ' + \
            '"--include-singletons", ' + \
            '"--first_attribute", "' + "DNA_Repair" + '",' \
            '"--no_layout_independent_stats", ' + \
            '"--no_layout_aware_stats" ]'
        
        curl_opts = ['-d', data, '-H', 'Content-Type:application/json', '-X', 'POST', '-v']
        rc = s.doCurl(curl_opts)
        #print 'code, data:', rc['code'], rc['data']
        s.assertTrue(rc['code'] == '200')
        success = s.checkLog(outDir + 'log')
        s.assertTrue(success, True)

if __name__ == '__main__':
    unittest.main()
