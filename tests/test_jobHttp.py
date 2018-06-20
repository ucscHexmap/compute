#!/usr/bin/env python2.7

# This tests the job functionality via http.
# NOTE: these tests don't work under the centOS servers but do on the macOS.

import os
import datetime
import json, requests, time

import www
import unittest
import testUtil as util
from jobQueue import JobQueue
from util_web import Context

# TODO create a dir: out
testDir = os.getcwd()
quePath = os.path.join(os.getcwd() , 'out/jobQueue.db') # database file name
serverQueuePath = os.path.join(os.environ['HEX_CALC'], '../computeDb/jobQueue.db')
serverRoot = 'http://'
appCtx = Context({})
if os.environ['USE_HTTPS'] == '1':
    serverRoot = 'https://'
    appCtx.sslCert = os.environ['CERT']
    appCtx.sslKey = os.environ['KEY'],
serverRoot += os.environ['WWW_SOCKET']

# Results
result1 = {'myResult':'result1'}
result1unicode = json.loads(json.dumps(result1))

# Error message
errorMsg1 = {"error": "some error"}
errorMsg1trace = {"error": "some error", "stackTrace": "some stackTrace"}

# Seconds to wait for test job to complete
wait = 0.2

retryLimit = 10

class Test_jobHttp(unittest.TestCase):

    def postQuery(s, operation, data):
        '''
        return s.app.post(
            serverRoot + '/query/' + operation,
            data=json.dumps(data),
            headers={'Content-type': 'application/json'}
        )
        '''
        return requests.post(
            serverRoot + '/query/' + operation,
            data = json.dumps(data),
            verify = True,
            #cert = (appCtx.sslCert, appCtx.sslKey),
            headers = { 'Content-type': 'application/json' }
            #headers = { 'Content-type': 'application/json',  'retryLimit': str(retryLimit) }
        )
    
    def get(s, route):
        return requests.get(
            serverRoot + route,
            verify = True,
            #cert = (appCtx.sslCert, appCtx.sslKey),
            headers = { 'Content-type': 'application/json' },
        )

    def setUp(s):
        try:
            #os.remove(quePath)
            os.remove(serverQueuePath)
        except:
            pass
        www.app.config['UNIT_TEST'] = True
        s.app = www.app.test_client()
        s.que = JobQueue(quePath)

    def test_dataServerConnection(s):
        try:
            r = s.get('/test')
            #r = s.get('/test')
        except:
            s.assertEqual('', 'Unable to connect to the data server: ' +
                serverRoot + '. Is it up?')
        
        rData = json.loads(r.text)
        #print 'r.status_code', r.status_code
        #print 'r.text:', r.text
        #print 'rData:', rData
        s.assertEqual(r.status_code, 200)
        s.assertEqual('just testing data server', rData)
    
    def test_getStatusInJobQueue(s):
        s.postQuery('jobTestHelper', {'testStatus': s.que.inJobQueueSt})
        r = s.get('/jobStatus/jobId/1')
        rData = json.loads(r.text)
        #print 'test_getStatusInJobQueue():r.status_code:', r.status_code
        #print "test_getStatusInJobQueue():rData:", rData
        s.assertEqual(r.status_code, 200)
        s.assertEqual('InJobQueue', rData['status'])
        s.assertFalse('result' in rData)

    def test_getStatusRunning(s):
        s.postQuery('jobTestHelper', {'testStatus': s.que.runningSt})
        time.sleep(wait)
        r = s.get('/jobStatus/jobId/1')
        rData = json.loads(r.text)
        #print 'r.status_code:', r.status_code
        #print "rData:", rData
        s.assertEqual(r.status_code, 200)
        s.assertEqual(s.que.runningSt, rData['status'])
        s.assertFalse('result' in rData)

    def test_getStatusSuccess(s):
        s.postQuery('jobTestHelper', {'testStatus': s.que.successSt})
        time.sleep(wait)
        r = s.get('/jobStatus/jobId/1')
        rData = json.loads(r.text)
        #print 'r.status_code:', r.status_code
        #print "rData:", rData
        s.assertTrue(r.status_code == 200)
        s.assertEqual(s.que.successSt, rData['status'])
        s.assertFalse('result' in rData)
    
    def test_getStatusSuccessResult(s):
        s.postQuery('jobTestHelper', {'testStatus': s.que.successSt + 'Result'})
        time.sleep(wait)
        r = s.get('/jobStatus/jobId/1')
        rData = json.loads(r.text)
        #print 'r.status_code:', r.status_code
        #print "rData:", rData
        s.assertTrue(
            r.status_code == 200,
            util.message(r.status_code, 200)
        )
        s.assertEqual(s.que.successSt, rData['status'])
        s.assertTrue('result' in rData)
        s.assertEqual(result1, rData['result'])

    def test_getStatusError(s):
        s.postQuery('jobTestHelper', {'testStatus': s.que.errorSt})
        time.sleep(wait)
        r = s.get('/jobStatus/jobId/1')
        rData = json.loads(r.text)
        #print 'r.status_code:', r.status_code
        #print "rData:", rData
        s.assertTrue(r.status_code == 200)
        s.assertEqual(s.que.errorSt, rData['status'])
        s.assertFalse('result' in rData)

    def test_getStatusErrorResult(s):
        s.postQuery('jobTestHelper', {'testStatus': s.que.errorSt + 'Result'})
        time.sleep(wait)
        r = s.get('/jobStatus/jobId/1')
        rData = json.loads(r.text)
        #print 'r.status_code:', r.status_code
        #print "rData:", rData
        s.assertTrue(r.status_code == 200)
        s.assertEqual(s.que.errorSt, rData['status'])
        s.assertTrue('result' in rData)
        s.assertEqual(errorMsg1, rData['result'])

    def test_getStatusErrorTrace(s):
        s.postQuery('jobTestHelper', {'testStatus': s.que.errorSt + 'Trace'})
        time.sleep(wait)
        r = s.get('/jobStatus/jobId/1')
        rData = json.loads(r.text)
        #print 'r.status_code:', r.status_code
        #print "rData:", rData
        s.assertTrue(r.status_code == 200)
        s.assertEqual(s.que.errorSt, rData['status'])
        s.assertTrue('result' in rData)
        s.assertEqual(errorMsg1trace, rData['result'])

    def test_getStatusInvalidJobId(s):
        r = s.get('/jobStatus/jobId/1')
        rData = json.loads(r.text)
        #print 'r.status_code:', r.status_code
        #print "json.loads(r.text):", json.loads(r.text)
        s.assertTrue(r.status_code == 400)
        s.assertEqual({'error': 'unknown job ID of: 1'}, rData)

if __name__ == '__main__':
    unittest.main()
