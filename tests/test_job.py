#!/usr/bin/env python2.7

# This tests the job queue and job runner.

import os
import datetime
import json

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

# Job context
ctx2 = 'ctx2'
ctx3 = 'ctx3'

appCtxDict = {'jobQueuePath': quePath, 'unitTest': True}
appCtx = Context(appCtxDict)
appCtxUnicode = json.loads(json.dumps(appCtxDict))

ctx1NoAppUnicode = json.loads(json.dumps({'prop1': 1}))
ctxdict = {'app': appCtx}
ctx1 = Context(ctxdict)
ctx1.prop1 = 1
ctx2 = Context(ctxdict)
ctx2.prop2 = 2
ctx3 = Context(ctxdict)
ctx3.prop3 = 3

# Tasks to execute as stored in the queue.
task1 = '{"ctx":{"app":{"jobQueuePath":"' + quePath + '","unitTest":true},"prop1":1},"operation":"jobTestHelper","parms":{"parms1":"parms1"}}'
task2 = '{"ctx":{"app":{"jobQueuePath":"' + quePath + '","unitTest":true},"prop2":2},"operation":"operation2","parms":"parms2"}'
task3 = '{"ctx":{"app":{"jobQueuePath":"' + quePath + '","unitTest":true},"prop3":3},"operation":"operation3","parms":"parms3"}'

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
errorMsg1 = '{"error": "some error"}'
errorMsg1trace = '{"error": "some error", "stackTrace": "some stackTrace"}'
errorMsg2 = 'errorMsg2'
errorMsg2 = 'errorMsg3'

# Test operation
operation1 = 'jobTestHelper'
operation2 = 'operation2'
operation3 = 'operation3'

# Parameters to a calc operation
parms1 = {"parms1":"parms1"}
parms2 = 'parms2'
parms3 = 'parms3'

today = str(datetime.date.today())

class Test_job(unittest.TestCase):

    def setUp(self):
        try:
            os.remove(quePath)
        except:
            pass
        self.que = JobQueue(quePath)
        self.runner = JobRunner(quePath)

    def test_packTask(s):
        packed = s.runner._packTask(operation1, parms1, ctx1);
        s.assertEqual(task1, packed)
    
    def test_unpackTask(s):
        packed = s.runner._packTask(operation1, parms1, ctx1)
        ctx, operation, parms = s.runner._unpackTask(packed)
        #print 'operation, parms, ctx:', operation, parms, ctx
        s.assertEqual(operation1, operation)
        s.assertEqual(parms1, parms)

        # Check the app Context class instance.
        #print 'appCtxUnicode:', appCtxUnicode
        #print 'ctx.app:', ctx.app
        s.assertEqual(str(appCtxUnicode), str(ctx.app))

        # Check the job Context class instance, minus the app context.
        del ctx.app
        s.assertEqual(str(ctx1NoAppUnicode), str(ctx))
    
    def test_add(s):
        r = runner.add(user1, operation1, parms1, ctx1)
        task1 = s.runner._packTask(operation1, parms1, ctx1);

        # Verify correct job ID & status was returned.
        s.assertEqual(1, r['jobId']);
        s.assertEqual(s.que.inJobQueueSt, r['status']);
        
        # Verify fields were initialized properly.
        out = s.que._getOne(1)
        #print 'out:', out
        s.assertEqual(s.que.inJobQueueSt, out[s.que.statusI])
        s.assertEqual(user1, out[s.que.userI])
        s.assertEqual(today, out[s.que.lastAccessI])
        s.assertEqual(None, out[s.que.processIdI])
        s.assertEqual(task1, out[s.que.taskI])
        s.assertEqual(None, out[s.que.resultI])

    def test_getOne(s):
        runner.add(user1, operation1, parms1, ctx1);
        job = s.que._getOne(1)
        s.assertEqual(1, job[s.que.idI])
    
    def test_getOneWithNone(s):
        job = s.que._getOne(1)
        s.assertEqual(None, job)
    
    def test__getStatus(s):
    
        # Test the private _getStatus()
        runner.add(user1, operation1, parms1, ctx1);
        r = s.que._getStatus(1)
        s.assertEqual(s.que.inJobQueueSt, r['status']);
        s.assertFalse('result' in r)

    def test__getStatusBadJobId(s):
    
        # Test the private _getStatus() for unknown job ID
        r = s.que._getStatus(1)
        s.assertEqual(None, r);
    
    def test_getStatusInJobQueue(s):

        # Test the public getStatus()
        runner.add(user1, operation1, parms1, ctx1);
        r = que.getStatus(1, quePath)
        s.assertEqual(s.que.inJobQueueSt, r['status']);
        s.assertFalse('result' in r)

    def test_getStatusRunning(s):
        runner.add(user1, operation1, parms1, ctx1);
        s.runner._setDoneStatus(1, s.que.runningSt)
        r = que.getStatus(1, quePath)
        #print 'r:', r
        s.assertEqual(s.que.runningSt, r['status']);
        s.assertFalse('result' in r)

    def test_getStatusSuccess(s):
        runner.add(user1, operation1, parms1, ctx1);
        s.runner._setDoneStatus(1, s.que.successSt, result1)
        r = que.getStatus(1, quePath)
        #print 'r:', r
        s.assertEqual(s.que.successSt, r['status']);
        #s.assertEqual(json.dumps('result1'), r['result']);
        s.assertEqual(result1, r['result']);

    def test_getStatusError(s):
        runner.add(user1, operation1, parms1, ctx1);
        s.runner._setDoneStatus(1, s.que.errorSt, errorMsg1)
        r = que.getStatus(1, quePath)
        s.assertEqual(s.que.errorSt, r['status']);
        s.assertEqual(errorMsg1, r['result']);

    def test_getStatusErrorWithTrace(s):
        runner.add(user1, operation1, parms1, ctx1);
        s.runner._setDoneStatus(1, s.que.errorSt, errorMsg1trace)
        r = que.getStatus(1, quePath)
        s.assertEqual(s.que.errorSt, r['status']);
        s.assertEqual(errorMsg1trace, r['result']);

    def test_getAll(s):
        runner.add(user1, operation1, parms1, ctx1);
        runner.add(user2, operation2, parms2, ctx2);
        runner.add(user3, operation3, parms3, ctx3);
        s.runner._setDoneStatus(1, s.que.successSt, result1)
        s.runner._setDoneStatus(2, s.que.errorSt, errorMsg1)
        rows = s.que._getAll()
        #print 'rows[0]:', rows[0]

        # Verify all fields in job1.
        s.assertEqual(1, rows[0][s.que.idI])
        s.assertEqual(s.que.successSt, rows[0][s.que.statusI])
        s.assertEqual(user1, rows[0][s.que.userI])
        s.assertEqual(today, rows[0][s.que.lastAccessI])
        s.assertEqual(None, rows[0][s.que.processIdI])
        #print '              task1:', task1
        #print 'rows[0][s.que.taskI]:',rows[0][s.que.taskI]
        resultUnjson = json.loads(rows[0][s.que.resultI])
        s.assertEqual(task1, rows[0][s.que.taskI])
        s.assertEqual(result1unicode, resultUnjson)

        # Verify all fields in job2.
        s.assertEqual(2, rows[1][s.que.idI])
        s.assertEqual(s.que.errorSt, rows[1][s.que.statusI])
        s.assertEqual(user2, rows[1][s.que.userI])
        s.assertEqual(today, rows[1][s.que.lastAccessI])
        s.assertEqual(None, rows[1][s.que.processIdI])
        s.assertEqual(task2, rows[1][s.que.taskI])
        resultUnjson = json.loads(rows[1][s.que.resultI])
        s.assertEqual(errorMsg1, resultUnjson)

        # Verify all fields in job3.
        s.assertEqual(3, rows[2][s.que.idI])
        s.assertEqual(s.que.inJobQueueSt, rows[2][s.que.statusI])
        s.assertEqual(user3, rows[2][s.que.userI])
        s.assertEqual(today, rows[2][s.que.lastAccessI])
        s.assertEqual(None, rows[2][s.que.processIdI])
        s.assertEqual(task3, rows[2][s.que.taskI])
        s.assertEqual(None, rows[2][s.que.resultI])

    def test_getAllWhenNone(s):
        rows = s.que._getAll()
        s.assertEqual([], rows)

    def test_getNextToRun(s):
        runner.add(user1, operation1, parms1, ctx1);
        job = s.runner._getNextToRun()
        s.assertEqual(1, job[s.que.idI]);

    def test_getNextToRunWhenNone(s):
        job = s.runner._getNextToRun()
        s.assertEqual(None, job);

    def test_runner(s):
        runner.add(user1, operation1, parms1, ctx1)
        s.runner._runner(1, task1)
        r = s.que._getStatus(1)
        #print 'r:', r
        s.assertEqual('Success', r['status'])
        s.assertEqual(result1, r['result'])
    
if __name__ == '__main__':
    unittest.main()
