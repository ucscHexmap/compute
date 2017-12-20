#!/usr/bin/env python2.7

# This tests the job queue and job runner via http.

import os
import datetime
import json, requests, time

import unittest
import testUtil as util
from jobRunner import JobRunner
import jobRunner as runner
from jobQueue import JobQueue
import jobQueue as que
from util_web import Context

# TODO create a dir: out
testDir = os.getcwd()
quePath = os.path.join(os.getcwd() , 'out/jobQueue.db') # database file name
serverQueuePath = os.path.join(os.environ['HUB_PATH'], '../computeDb/jobQueue.db')
wwwSocket = os.environ['WWW_SOCKET']

# Results
result1 = {'myResult':'result1'}
result1unicode = json.loads(json.dumps(result1))

# Error message
errorMsg1 = {"error": "some error"}
errorMsg1trace = {"error": "some error", "stackTrace": "some stackTrace"}

# Seconds to wait for test job to complete
wait = 0.1

class Test_jobHttp(unittest.TestCase):

    def postQuery(s, operation, data):
        return requests.post(
            'http://' + wwwSocket + '/query/' + operation,
            data = json.dumps(data),
            #cert=(ctx['sslCert'], ctx['sslKey']),
            verify=False,
            headers = { 'Content-type': 'application/json' },
        )
        
    def get(s, route):
        return requests.get(
            'http://' + wwwSocket + route,
            #cert=(ctx['sslCert'], ctx['sslKey']),
            verify=False,
            headers = { 'Content-type': 'application/json' },
        )

    def setUp(s):
        try:
            os.remove(quePath)
            os.remove(serverQueuePath)
        except:
            pass
        s.que = JobQueue(quePath)
        s.runner = JobRunner(quePath)
        
        #s.postQuery('jobTestHelper', {'testStatus': s.que.inJobQueueSt})
        #s.postQuery('jobTestHelper', {'testStatus': s.que.runningSt})
        '''
        s.postQuery('jobTestHelper', {'testStatus': s.que.successSt})
        s.postQuery('jobTestHelper', {'testStatus': s.que.successSt + 'Result'})
        s.postQuery('jobTestHelper', {'testStatus': s.que.errorSt})
        s.postQuery('jobTestHelper', {'testStatus': s.que.errorSt + 'Result'})
        s.postQuery('jobTestHelper', {'testStatus': s.que.errorSt + 'Trace'})
        '''

    def test_dataServerConnection(s):
        url = 'http://' + wwwSocket + '/test'
        try:
            r = requests.get(
                url,
                #cert=(ctx['sslCert'], ctx['sslKey']),
                verify=False,
                headers = { 'Content-type': 'application/json' },
            )
        except:
            s.assertEqual('', 'Unable to connect to the data server: ' +
                wwwSocket + '. Is it up?')
        
        rText = json.loads(r.text)
        #print 'r.text:', r.text
        #print 'rText:', rText
        s.assertEqual(r.status_code, 200)
        s.assertEqual('just testing data server', rText)

    def test_postQuery(s):
        r = s.postQuery('jobTestHelper', {'testStatus': s.que.inJobQueueSt})
        rText = json.loads(r.text)
        #print 'setUp():rText:', rText
        s.assertEqual(r.status_code, 200)
        s.assertEqual('InJobQueue', rText['status'])
        s.assertEqual(1, rText['jobId'])

    def test_getAllJobs(s):
        s.postQuery('jobTestHelper', {'testStatus': s.que.successSt})
        s.postQuery('jobTestHelper', {'testStatus': s.que.errorSt})
        r = s.get('/getAllJobs')
        rText = json.loads(r.text)
        #print 'rText:', rText
        s.assertEqual(1, rText['jobs'][0][0])
        s.assertEqual(2, rText['jobs'][1][0])

    def test_getStatusInJobQueue(s):
        s.postQuery('jobTestHelper', {'testStatus': s.que.inJobQueueSt})
        r = requests.get(
            'http://' + wwwSocket + '/jobStatus/jobId/1',
            #cert=(ctx['sslCert'], ctx['sslKey']),
            verify=False,
            headers = { 'Content-type': 'application/json' },
        )
        rText = json.loads(r.text)
        #print 'test_getStatusInJobQueue():r.status_code:', r.status_code
        #print "test_getStatusInJobQueue():rText:", rText
        s.assertEqual(r.status_code, 200)
        s.assertEqual('InJobQueue', rText['status'])
        s.assertFalse('result' in rText)

    def test_getStatusRunning(s):
        s.postQuery('jobTestHelper', {'testStatus': s.que.runningSt})
        r = requests.get(
            'http://' + wwwSocket + '/jobStatus/jobId/1',
            #cert=(ctx['sslCert'], ctx['sslKey']),
            verify=False,
            headers = { 'Content-type': 'application/json' },
        )
        rText = json.loads(r.text)
        #print 'r.status_code:', r.status_code
        #print "rText:", rText
        s.assertEqual(r.status_code, 200)
        s.assertEqual(s.que.runningSt, rText['status'])
        s.assertFalse('result' in rText)

    def test_getStatusSuccess(s):
        s.postQuery('jobTestHelper', {'testStatus': s.que.successSt})
        time.sleep(wait)
        r = requests.get(
            'http://' + wwwSocket + '/jobStatus/jobId/1',
            #cert=(ctx['sslCert'], ctx['sslKey']),
            verify=False,
            headers = { 'Content-type': 'application/json' },
        )
        rText = json.loads(r.text)
        #print 'r.status_code:', r.status_code
        #print "rText:", rText
        s.assertTrue(r.status_code == 200)
        s.assertEqual(s.que.successSt, rText['status'])
        s.assertFalse('result' in rText)
    
    def test_getStatusSuccessResult(s):
        s.postQuery('jobTestHelper', {'testStatus': s.que.successSt + 'Result'})
        time.sleep(wait)
        r = requests.get(
            'http://' + wwwSocket + '/jobStatus/jobId/1',
            #cert=(ctx['sslCert'], ctx['sslKey']),
            verify=False,
            headers = { 'Content-type': 'application/json' },
        )
        rText = json.loads(r.text)
        #print 'r.status_code:', r.status_code
        #print "rText:", rText
        s.assertTrue(r.status_code == 200)
        s.assertEqual(s.que.successSt, rText['status'])
        s.assertTrue('result' in rText)
        s.assertEqual(result1, rText['result'])

    def test_getStatusError(s):
        s.postQuery('jobTestHelper', {'testStatus': s.que.errorSt})
        time.sleep(wait)
        r = requests.get(
            'http://' + wwwSocket + '/jobStatus/jobId/1',
            #cert=(ctx['sslCert'], ctx['sslKey']),
            verify=False,
            headers = { 'Content-type': 'application/json' },
        )
        rText = json.loads(r.text)
        #print 'r.status_code:', r.status_code
        #print "rText:", rText
        s.assertTrue(r.status_code == 200)
        s.assertEqual(s.que.errorSt, rText['status'])
        s.assertFalse('result' in rText)

    def test_getStatusErrorResult(s):
        s.postQuery('jobTestHelper', {'testStatus': s.que.errorSt + 'Result'})
        time.sleep(wait)
        r = requests.get(
            'http://' + wwwSocket + '/jobStatus/jobId/1',
            #cert=(ctx['sslCert'], ctx['sslKey']),
            verify=False,
            headers = { 'Content-type': 'application/json' },
        )
        rText = json.loads(r.text)
        #print 'r.status_code:', r.status_code
        #print "rText:", rText
        s.assertTrue(r.status_code == 200)
        s.assertEqual(s.que.errorSt, rText['status'])
        s.assertTrue('result' in rText)
        s.assertEqual(errorMsg1, rText['result'])

    def test_getStatusErrorTrace(s):
        s.postQuery('jobTestHelper', {'testStatus': s.que.errorSt + 'Trace'})
        time.sleep(wait)
        r = s.get('/jobStatus/jobId/1')
        rText = json.loads(r.text)
        #print 'r.status_code:', r.status_code
        #print "rText:", rText
        s.assertTrue(r.status_code == 200)
        s.assertEqual(s.que.errorSt, rText['status'])
        s.assertTrue('result' in rText)
        s.assertEqual(errorMsg1trace, rText['result'])

    def test_getStatusInvalidJobId(s):
        r = s.get('/jobStatus/jobId/1')
        rText = json.loads(r.text)
        #print 'r.status_code:', r.status_code
        #print "json.loads(r.text):", json.loads(r.text)
        s.assertTrue(r.status_code == 400)
        s.assertEqual({'error': 'unknown job ID of: 1'}, rText)

if __name__ == '__main__':
    unittest.main()
