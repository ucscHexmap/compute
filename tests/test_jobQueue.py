#!/usr/bin/env python2.7

# This tests the jobQueue

"""
import sys, os, glob, subprocess, json, tempfile, pprint
from os import path
import string, requests
"""
import os
import unittest
import testUtil as util
from random import random
from jobQueue import JobQueue

# TODO create a dir: out
quePath = '/Users/swat/dev/compute/tests/out/jobQueue'

task1 = 'this is task #1'
task2 = 'and this is task #2'
task3 = 'yet another task #3'
task4 = 'one more task #4'

waitingToRun = 'waiting to run'
running = 'running'
success ='success'
error = 'error'

# Column indices when all columns are included.
idI = 0
statusI = 1
taskI = 2

class Task(object):
    def __init__(s, parm):
        s.jobId = parm['jobId']
        s.executable = parm['executable']
    def __str__(self):
        return 'jobId: ' + self.jobId + '\nexecutable: ' + self.executable
        #return '__str__ func of Task'

'''
class InvalidAction(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
'''

class Test_jobQueue(unittest.TestCase):

    def setUp(self):
        os.remove(quePath)
        self.que = JobQueue(quePath)

    def test_push(s):
        result = s.que.push(task1);
        expected = 1
        s.assertEqual(expected, result);

    def test_getAll(s):
        s.que.push(task1);
        s.que.push(task2);

        # Result should be an iterable
        result = s.que.getAll()
        #print 'result:', result
        rows = []
        for id, status, task in result:
            rows.append([id, status, task])
        #print 'rows:', rows
        s.assertEqual(1, rows[0][idI])
        s.assertEqual(waitingToRun, rows[0][statusI])
        s.assertEqual(task1, rows[0][taskI])
        s.assertEqual(2, rows[1][idI])
        s.assertEqual(waitingToRun, rows[1][statusI])
        s.assertEqual(task2, rows[1][taskI])

    def test_getStatus(s):
        s.que.push(task1);
        s.que.push(task2);
        result = s.que.getStatus(2)
        #print 'result:', result
        s.assertEqual(waitingToRun, result)

    def test_setStatus(s):
        s.que.push(task1);
        s.que.push(task2);
        s.que.setStatus(2, success)
        #print 'result:', result
        result = s.que.getStatus(2)
        #print 'result:', result
        s.assertEqual(success, result)

    def test_getNextToRun(s):
        s.que.push(task1);
        s.que.push(task2);
        s.que.push(task3);
        s.que.push(task4);
        s.que.setStatus(1, running)
        s.que.setStatus(2, success)
        result = s.que.getNextToRun()
        #print 'result:', result
        s.assertEqual(result[idI], 1)
        s.assertEqual(result[taskI], task3)
        s.assertEqual(result[statusI], running)



if __name__ == '__main__':
    unittest.main()
