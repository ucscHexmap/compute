#!/usr/bin/env python2.7

# This tests the job queue and job runner.

import os
import datetime
import unittest
import testUtil as util
from jobRunner import JobRunner
from jobQueue import JobQueue

# TODO create a dir: out
testDir = os.getcwd()
quePath = os.path.join(os.getcwd() , 'out/jobQueue.db') # database file name

# Tasks to execute.
task1 = '{"ctx":"ctx1","operation":"testOperation1","parms":"parms1"}'
task2 = '{"ctx":"ctx2","operation":"operation2","parms":"parms2"}'
task3 = '{"ctx":"ctx3","operation":"operation3","parms":"parms3"}'

# Usernames
user1 = 'user1'
user2 = 'user2'
user3 = 'user3'

# Results
result1 = 'result1'
result2 = 'result2'
result3 = 'result3'

# Error message
errorMsg1 = 'errorMsg1'
errorMsg2 = 'errorMsg2'
errorMsg2 = 'errorMsg3'

# Test operation
operation1 = 'testOperation1'
operation2 = 'operation2'
operation3 = 'operation3'

# Parameters to a calc operation
parms1 = 'parms1'
parms2 = 'parms2'
parms3 = 'parms3'

# Www context
ctx1 = 'ctx1'
ctx2 = 'ctx2'
ctx3 = 'ctx3'

today = str(datetime.date.today())

class Test_job(unittest.TestCase):

    def setUp(self):
        try:
            os.remove(quePath)
        except:
            pass
        self.jq = JobQueue(quePath)
        self.jr = JobRunner(quePath)

    def test_add(s):
        jobId, status = \
            s.jq.add(user1, operation1, parms1, ctx1, waitForPoll=True);

        # Verify correct job ID & status was returned.
        s.assertEqual(1, jobId);
        s.assertEqual(s.jq.inJobQueueSt, status);
        
        # Verify fields were initialized properly.
        out = s.jq._getOne(1)
        #print 'out:', out
        s.assertEqual(s.jq.inJobQueueSt, out[s.jq.statusI])
        s.assertEqual(user1, out[s.jq.userI])
        s.assertEqual(today, out[s.jq.lastAccessI])
        s.assertEqual(None, out[s.jq.processIdI])
        s.assertEqual(task1, out[s.jq.taskI])
        s.assertEqual(None, out[s.jq.resultI])
        
    def test_getOne(s):
        s.jq.add(user1, operation1, parms1, ctx1, waitForPoll=True);
        job = s.jq._getOne(1)
        s.assertEqual(1, job[s.jq.idI])
    
    def test_getOneWithNone(s):
        job = s.jq._getOne(1)
        s.assertEqual(None, job)
    
    def test_getStatus(s):
        s.jq.add(user1, operation1, parms1, ctx1, waitForPoll=True);
        status, result = s.jq.getStatus(1)
        s.assertEqual(s.jq.inJobQueueSt, status);
        s.assertEqual(None, result);
    
    def test_getStatusWithNone(s):
        job = s.jq.getStatus(1)
        s.assertEqual(None, job)
    
    def test_getAll(s):
        s.jq.add(user1, operation1, parms1, ctx1, waitForPoll=True);
        s.jq.add(user2, operation2, parms2, ctx2, waitForPoll=True);
        s.jq.add(user3, operation3, parms3, ctx3, waitForPoll=True);
        s.jr._setResult(1, s.jq.successSt, result1)
        s.jr._setResult(2, s.jq.errorSt, errorMsg1)
        rows = s.jq._getAll()
        #print 'rows[0]:', rows[0]

        # Verify all fields in job1.
        s.assertEqual(1, rows[0][s.jq.idI])
        s.assertEqual(s.jq.successSt, rows[0][s.jq.statusI])
        s.assertEqual(user1, rows[0][s.jq.userI])
        s.assertEqual(today, rows[0][s.jq.lastAccessI])
        s.assertEqual(None, rows[0][s.jq.processIdI])
        s.assertEqual(task1, rows[0][s.jq.taskI])
        s.assertEqual(result1, rows[0][s.jq.resultI])

        # Verify all fields in job2.
        s.assertEqual(2, rows[1][s.jq.idI])
        s.assertEqual(s.jq.errorSt, rows[1][s.jq.statusI])
        s.assertEqual(user2, rows[1][s.jq.userI])
        s.assertEqual(today, rows[1][s.jq.lastAccessI])
        s.assertEqual(None, rows[1][s.jq.processIdI])
        s.assertEqual(task2, rows[1][s.jq.taskI])
        s.assertEqual(errorMsg1, rows[1][s.jq.resultI])

        # Verify all fields in job3.
        s.assertEqual(3, rows[2][s.jq.idI])
        s.assertEqual(s.jq.inJobQueueSt, rows[2][s.jq.statusI])
        s.assertEqual(user3, rows[2][s.jq.userI])
        s.assertEqual(today, rows[2][s.jq.lastAccessI])
        s.assertEqual(None, rows[2][s.jq.processIdI])
        s.assertEqual(task3, rows[2][s.jq.taskI])
        s.assertEqual(None, rows[2][s.jq.resultI])

    def test_getAllWhenNone(s):
        rows = s.jq._getAll()
        s.assertEqual([], rows)
    
    def test_packTask(s):
        packed = s.jq._packTask(operation1, parms1, ctx1);
        s.assertEqual(task1, packed)
    
    def test_unpackTask(s):
        packed = task1
        operation, parms, ctx = s.jr._unpackTask(packed)
        #print 'operation, parms, ctx:', operation, parms, ctx
        s.assertEqual(operation1, operation)
        s.assertEqual(parms1, parms)
        s.assertEqual(ctx1, ctx)
    
    def test_getNextToRun(s):
        s.jq.add(user1, operation1, parms1, ctx1, waitForPoll=True);
        job = s.jr._getNextToRun()
        s.assertEqual(1, job[s.jq.idI]);

    def test_getNextToRunWhenNone(s):
        job = s.jr._getNextToRun()
        s.assertEqual(None, job);
    
    def test_runner(s):
        s.jq.add(user1, operation1, parms1, ctx1, waitForPoll=True)
        s.jr._runner(1, task1, 'jobTestHelper')
        status, result = s.jq.getStatus(1)
        s.assertEqual(s.jq.successSt, status)
        s.assertEqual(result1, result)
    
if __name__ == '__main__':
    unittest.main()
