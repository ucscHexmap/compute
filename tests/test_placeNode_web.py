import os, json, requests
import unittest
import testUtil
import www
import placeNode_web
import job
import jobProcess
from jobProcess import JobProcess
from jobQueue import JobQueue
from util_web import Context

# Job runner contexts
quePath = os.path.join(os.getcwd() , 'out/placeNodeJobQueue.db') # database file name
jobStatusUrl = 'http://127.0.0.1:5000/jobStatus/jobId/'

appCtxDict = {
    'adminEmail': os.environ.get('ADMIN_EMAIL'),
    'dataRoot': 'in/dataRoot',
    'debug': os.environ.get('DEBUG', 0),
    'dev': int(os.environ.get('DEV', 0)),
    'hubPath': os.environ.get('HUB_PATH'),
    'jobQueuePath': quePath,
    'jobStatusUrl': jobStatusUrl,
    'unitTest': int(os.environ.get('UNIT_TEST', 0)),
    'viewServer': os.environ.get('VIEWER_URL', 'http://hexdev.sdsc.edu'),
}
appCtxDict['jobQueuePath'] = os.path.join(quePath)
appCtxDict['viewDir'] = os.path.join(appCtxDict['dataRoot'], 'view')
appCtx = Context(appCtxDict)
appCtxUnicode = json.loads(json.dumps(appCtxDict))
ctx1NoAppUnicode = json.loads(json.dumps({'prop1': 1}))
ctxdict = {'app': appCtx}
ctx1 = Context(ctxdict)
ctx1.prop1 = 1

class Test_placeNode(unittest.TestCase):

    # This view server must be running for these tests.
    viewServer = os.environ['VIEWER_URL']
    unprintable = '09'.decode('hex')  # tab character

    def setUp(self):
        self.app = www.app.test_client()
        try:
            os.remove(quePath)
        except:
            pass
        self.jobQueue = JobQueue(quePath)

    def tearDown(self):
        pass

    def test_get_not_allowed(s):
        rv = s.app.get('/query/overlayNodes')
        s.assertTrue(rv.status_code == 405)

    def test_content_type_not_json(s):
        rv = s.app.post('/query/overlayNodes',
            #content_type='application/json',
            data=dict(
                username='username',
                password='password',
            )
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        s.assertTrue(rv.status_code == 400)
        s.assertTrue(data['error'] == 'Content-Type must be application/json')

    def test_invalid_json(s):
        rv = s.app.post('/query/overlayNodes',
            content_type='application/json',
            data=dict(
                map='someMapId',
            )
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        s.assertTrue(rv.status_code == 400)
        s.assertTrue(data['error'] == 'Post content is invalid JSON')
    
    def test_no_map(s):
        rv = s.app.post('/query/overlayNodes',
            content_type='application/json',
            data=json.dumps(dict(
                someData='someData',
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print "rv.status_code", rv.status_code
        #print "data['error']", data['error']
        s.assertTrue(rv.status_code == 400)
        s.assertTrue(data['error'] == 'map parameter missing or malformed')
    
    def test_map_not_string(s):
        rv = s.app.post('/query/overlayNodes',
            content_type='application/json',
            data=json.dumps(dict(
                map=1,
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        s.assertTrue(rv.status_code == 400)
        s.assertTrue(data['error'] ==
            'map parameter should be a string')
    
    def test_map_length_of_zero(s):
        rv = s.app.post('/query/overlayNodes',
            content_type='application/json',
            data=json.dumps(dict(
                map='',
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        s.assertTrue(rv.status_code == 400)
        s.assertTrue(data['error'] ==
            'map parameter must have a string length greater than one')
    
    def test_map_not_printable_chars(s):
        rv = s.app.post('/query/overlayNodes',
            content_type='application/json',
            data=json.dumps(dict(
                map='s' + s.unprintable + 'ssx'
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print "rv.status_code", rv.status_code
        #print "data['error']", data['error']
        s.assertTrue(rv.status_code == 400)
        s.assertTrue(data['error'] ==
            'map parameter should only contain printable characters')
    
    def test_map_multiple_slashes(s):
        rv = s.app.post('/query/overlayNodes',
            content_type='application/json',
            data=json.dumps(dict(
                map='s/s/s'
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print "rv.status_code", rv.status_code
        #print "data['error']", data['error']
        s.assertTrue(rv.status_code == 400)
        s.assertTrue(data['error'] ==
            'map IDs may not contain more than one slash')

    def test_map_not_file_safe_single(s):
        rv = s.app.post('/query/overlayNodes',
            content_type='application/json',
            data=json.dumps(dict(
                map='s:s'
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print "rv.status_code", rv.status_code
        #print "data['error']", data['error']
        s.assertTrue(rv.status_code == 400)
        s.assertTrue(data['error'] ==
            'map parameter may only contain the characters: ' + \
            'a-z, A-Z, 0-9, dash (-), dot (.), underscore (_), slash (/)')

    def test_map_not_file_safe_major(s):
        rv = s.app.post('/query/overlayNodes',
            content_type='application/json',
            data=json.dumps(dict(
                map='s:s/gg'
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print "rv.status_code", rv.status_code
        #print "data['error']", data['error']
        s.assertTrue(rv.status_code == 400)
        s.assertTrue(data['error'] ==
            'map parameter may only contain the characters: ' + \
            'a-z, A-Z, 0-9, dash (-), dot (.), underscore (_), slash (/)')

    def test_map_not_file_safe_minor(s):
        rv = s.app.post('/query/overlayNodes',
            content_type='application/json',
            data=json.dumps(dict(
                map='gg/s:s'
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print "rv.status_code", rv.status_code
        #print "data['error']", data['error']
        s.assertTrue(rv.status_code == 400)
        s.assertTrue(data['error'] ==
            'map parameter may only contain the characters: ' + \
            'a-z, A-Z, 0-9, dash (-), dot (.), underscore (_), slash (/)')

    def test_no_layout(s):
        rv = s.app.post('/query/overlayNodes',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        s.assertTrue(rv.status_code == 400)
        s.assertTrue(data['error'] == 'layout parameter missing or malformed')

    def test_layout_not_string(s):
        rv = s.app.post('/query/overlayNodes',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layout=1,
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        s.assertTrue(rv.status_code == 400)
        s.assertTrue(data['error'] ==
            'layout parameter should be a string')
    
    def test_no_nodes(s):
        rv = s.app.post('/query/overlayNodes',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layout='someLayout'
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        s.assertTrue(rv.status_code == 400)
        s.assertTrue(data['error'] == 'nodes parameter missing or malformed')

    def test_nodes_not_python_dict(s):
        rv = s.app.post('/query/overlayNodes',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layout='someLayout',
                nodes='someNodes'
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        s.assertTrue(rv.status_code == 400)
        s.assertTrue(data['error'] ==
            'nodes parameter should be a dictionary')

    def test_node_count_of_one_or_more(s):
        rv = s.app.post('/query/overlayNodes',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layout='someLayout',
                nodes = dict(
                ),
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        s.assertTrue(rv.status_code == 400)
        s.assertTrue(data['error'] ==
            'there are no nodes in the nodes dictionary')

    def test_email_not_python_string_or_list(s):
        rv = s.app.post('/query/overlayNodes',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layout='someLayout',
                nodes = dict(
                    someNode='someValue',
                ),
                email=1,
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print 'rv.status_code:', rv.status_code
        #print 'data[error]:', data['error']
        s.assertTrue(rv.status_code == 400)
        s.assertTrue(data['error'] ==
            'email parameter should be a string or an array of strings')

    def test_email_bad_chars_in_string(s):
        rv = s.app.post('/query/overlayNodes',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layout='someLayout',
                nodes = dict(
                    someNode='someValue',
                ),
                email='z' + s.unprintable + 'a',
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print 'rv.status_code:', rv.status_code
        #print 'data[error]:', data['error']
        s.assertTrue(rv.status_code == 400)
        s.assertTrue(data['error'] ==
            'email parameter should only contain printable characters')

    def test_email_bad_chars_in_array(s):
        rv = s.app.post('/query/overlayNodes',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layout='someLayout',
                nodes = dict(
                    someNode='someValue',
                ),
                email=['z' + s.unprintable + 'a'],
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print 'rv.status_code:', rv.status_code
        #print 'data[error]:', data['error']
        s.assertTrue(rv.status_code == 400)
        s.assertTrue(data['error'] ==
            'email parameter should only contain printable characters')

    def test_viewServer_not_string(s):
        rv = s.app.post('/query/overlayNodes',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layout='someLayout',
                nodes = dict(
                    someNode='someValue',
                ),
                email=['someone@somewhere'],
                viewServer=1,
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        s.assertTrue(rv.status_code == 400)
        #print "data['error']", data['error']
        s.assertTrue(data['error'] ==
            'viewServer parameter should be a string')

    def test_neighborCount_not_integer(s):
        rv = s.app.post('/query/overlayNodes',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layout='someLayout',
                nodes = dict(
                    someNode='someValue',
                ),
                email = ['someone@somewhere'],
                viewServer = s.viewServer,
                neighborCount='a',
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        s.assertTrue(rv.status_code == 400)
        #print "data['error']", data['error']
        s.assertTrue(data['error'] ==
            'neighborCount parameter should be a positive integer')
            
    def runJob (s, data):
    
        # Add the job to the queue.
        r = job.add('swat@soe.ucsc.edu', 'placeNode', data, ctx1)
        jobId = r['jobId']
        status = r['status']

        # A new process, so we need another instance of the job runner.
        myJobProcess = JobProcess(quePath)

        # Prepare the task in the same form as it is stored in the queue.
        task = job._packTask('placeNode', data, ctx1)

        # Execute the job.
        jobProcess.main([quePath, jobId])

        # Return the result of the job.
        return s.jobQueue.getStatus(1)

    def test_map_has_no_background_data(s):
        data = {
            'map': 'someMap',
            'layout': 'someLayout',
            'nodes': {
                'someNode': 'someValue',
            },
        }
        r = s.runJob(data)
        s.assertTrue(r['status'] == 'Error')
        #print 'r:', r
        #print "r['result']['error']:@@" + r['result']['error'] + '@@'
        expectedResult = \
            'Server error: Clustering data not found for layout: someLayout'
        s.assertEqual(expectedResult, r['result']['error'])
        s.assertTrue('stackTrace' in r['result'])

    def test_layout_has_no_background_data(s):
        data = {
            'map': 'unitTest/layoutBasicExp',
            'layout': 'someLayout',
            'nodes': {
                'someNode': 'someValue',
            },
        }
        r = s.runJob(data)
        s.assertTrue(r['status'] == 'Error')
        expectedResult = \
            'Server error: Clustering data not found for layout: someLayout'
        s.assertEqual(expectedResult, r['result']['error'])
        s.assertTrue('stackTrace' in r['result'])


    def test_create_bookmark(s):
        opts = [
            '-d', json.dumps(dict(
                page = 'mapPage',
                project = 'unitTest/layoutBasicExp/',
                layoutIndex = 0,
            )),
            '-H', 'Content-Type:application/json',
            '-X',
            'POST',
            '-v'
        ]
        rc = testUtil.doCurl(opts, s.viewServer + '/query/createBookmark')
        #print "rc['code']:", rc['code']
        s.assertTrue(rc['code'] == '200')
    
    def test_single_node_no_individual_urls(s):
    
        # Test that _postCalc() knows how to compose a bookmark from this data
        # returned from the calc routine.
        
        # Build the data input to the calc routine.
        dataIn = dict(
            map='unitTest/layoutBasicExp',
            layout='mRNA',
            nodes = dict(
                newNode1= {
                    'TP53': 0.54,
                    'ALK': 0.32,
                },
            ),
            testStub=True
        )
        
        # Build the calc result.
        ctx = Context({
            'app': appCtx,
            'dataIn': dataIn,
            'layoutIndex': 0,
        })
        result = {
            'nodes': {
                'newNode1': {
                    'x': 73,
                    'y': 91,
                    'neighbors': {
                        'TCGA-BP-4790': 0.352,
                        'TCGA-AK-3458': 0.742,
                    }
                }
            }
        }
        
        #print 'placeNode.test_single_node_no_individual_urls:result:', result
        #print 'placeNode.test_single_node_no_individual_urls:ctx:', ctx
        status, result = placeNode_web._postCalc(result, ctx)
        #print 'result:', result
        data = result
        
        s.assertTrue('newNode1' in data['nodes'])
        s.assertTrue('x' in data['nodes']['newNode1'])
        s.assertTrue(data['nodes']['newNode1']['x'] == 73)
        s.assertTrue('neighbors' in data['nodes']['newNode1'])
        s.assertTrue('TCGA-BP-4790' in data['nodes']['newNode1']['neighbors'])
        s.assertTrue(data['nodes']['newNode1']['neighbors']['TCGA-BP-4790'] == \
            0.352)
        bookmarkParm = '/?bookmark='
        sLen = len(s.viewServer) + len(bookmarkParm)
        s.assertTrue(data['nodes']['newNode1']['url'][:sLen] == \
            s.viewServer + bookmarkParm)
        
    
    def test_single_node_individual_urls_false(s):
    
        # Test that _postCalc() knows how to compose a bookmark from this data
        # returned from the calc routine.
        
        # Build the data input to the calc routine.
        dataIn = {
            'map': 'unitTest/layoutBasicExp',
            'layout': 'mRNA',
            'individualUrls': False,
            'nodes': {
                'newNode1': {
                    'TP53': 0.54,
                    'ALK': 0.32,
                },
            },
        }

        # Build the calc result.
        ctx = Context({
            'app': appCtx,
            'dataIn': dataIn,
            'layoutIndex': 0,
        })
        result = {
            'nodes': {
                'newNode1': {
                    'x': 73,
                    'y': 91,
                    'neighbors': {
                        'TCGA-BP-4790': 0.352,
                        'TCGA-AK-3458': 0.742,
                    }
                }
            }
        }
        status, result = placeNode_web._postCalc(result, ctx)
        #print 'result:', result
        data = result

        s.assertTrue('newNode1' in data['nodes'])
        s.assertTrue('x' in data['nodes']['newNode1'])
        s.assertTrue(data['nodes']['newNode1']['x'] == 73)
        s.assertTrue('neighbors' in data['nodes']['newNode1'])
        s.assertTrue('TCGA-BP-4790' in data['nodes']['newNode1']['neighbors'])
        s.assertTrue(data['nodes']['newNode1']['neighbors']['TCGA-BP-4790'] == \
            0.352)
        bookmarkParm = '/?bookmark='
        sLen = len(s.viewServer) + len(bookmarkParm)
        s.assertTrue(data['nodes']['newNode1']['url'][:sLen] == \
            s.viewServer + bookmarkParm)

    def test_single_node_individual_urls_true(s):
   
        # Test that _postCalc() knows how to compose a bookmark from this data
        # returned from the calc routine.
        
        # Build the data input to the calc routine.
        dataIn = {
            'map': 'unitTest/layoutBasicExp',
            'layout': 'mRNA',
            'individualUrls': True,
            'nodes': {
                'newNode1': {
                    'TP53': 0.54,
                    'ALK': 0.32,
                },
            },
        }

        # Build the calc result.
        ctx = Context({
            'app': appCtx,
            'dataIn': dataIn,
            'layoutIndex': 0,
        })
        result = {
            'nodes': {
                'newNode1': {
                    'x': 73,
                    'y': 91,
                    'neighbors': {
                        'TCGA-BP-4790': 0.352,
                        'TCGA-AK-3458': 0.742,
                    }
                }
            }
        }
        status, result = placeNode_web._postCalc(result, ctx)
        #print 'result:', result
        data = result
        s.assertTrue('newNode1' in data['nodes'])
        s.assertTrue('x' in data['nodes']['newNode1'])
        s.assertTrue(data['nodes']['newNode1']['x'] == 73)
        s.assertTrue('neighbors' in data['nodes']['newNode1'])
        s.assertTrue('TCGA-BP-4790' in data['nodes']['newNode1']['neighbors'])
        s.assertTrue(data['nodes']['newNode1']['neighbors']['TCGA-BP-4790'] == \
            0.352)
        bookmarkParm = '/?bookmark='
        sLen = len(s.viewServer) + len(bookmarkParm)
        s.assertTrue(data['nodes']['newNode1']['url'][:sLen] == \
            s.viewServer + bookmarkParm)

    def test_multi_nodes_no_individual_urls(s):
   
        # Test that _postCalc() knows how to compose a bookmark from this data
        # returned from the calc routine.
        
        # Build the data input to the calc routine.
        dataIn = {
            'map': 'unitTest/layoutBasicExp',
            'layout': 'mRNA',
            'nodes': {
                'newNode1': {
                    'TP53': 0.54,
                    'ALK': 0.32,
                },
                'newNode2': {
                    'TP53': 0.42,
                    'ALK': 0.36,
                },
            },
        }

        # Build the calc result.
        ctx = Context({
            'app': appCtx,
            'dataIn': dataIn,
            'layoutIndex': 0,
        })
        result = {
            'nodes': {
                'newNode1': {
                    'x': 73,
                    'y': 91,
                    'neighbors': {
                        'TCGA-BP-4790': 0.352,
                        'TCGA-AK-3458': 0.742,
                    }
                },
                'newNode2': {
                    'x': 53,
                    'y': 47,
                    'neighbors': {
                        'neighbor1': 0.567,
                        'neighbor2': 0.853,
                    }
                }
            }
        }
        status, result = placeNode_web._postCalc(result, ctx)
        #print 'result:', result
        data = result
        s.assertTrue('newNode1' in data['nodes'])
        s.assertTrue('newNode2' in data['nodes'])
        s.assertTrue('x' in data['nodes']['newNode1'])
        s.assertTrue(data['nodes']['newNode1']['x'] == 73)
        s.assertTrue('neighbors' in data['nodes']['newNode2'])
        s.assertTrue('TCGA-BP-4790' in data['nodes']['newNode1']['neighbors'])
        s.assertTrue(data['nodes']['newNode1']['neighbors']['TCGA-BP-4790'] == \
            0.352)
        bookmarkParm = '/?bookmark='
        sLen = len(s.viewServer) + len(bookmarkParm)
        s.assertTrue(
            data['nodes']['newNode1']['url'][:sLen] == \
            s.viewServer + bookmarkParm,
            msg=data['nodes']['newNode1']['url'][:sLen]
        )
        # urls for all nodes should be the same
        s.assertTrue(data['nodes']['newNode1']['url'] == \
            data['nodes']['newNode2']['url'])
            
    def test_multi_nodes_individual_urls_false(s):
   
        # Test that _postCalc() knows how to compose a bookmark from this data
        # returned from the calc routine.
        
        # Build the data input to the calc routine.
        dataIn = {
            'map': 'unitTest/layoutBasicExp',
            'layout': 'mRNA',
            'individualUrls': False,
            'nodes': {
                'newNode1': {
                    'TP53': 0.54,
                    'ALK': 0.32,
                },
                'newNode2': {
                    'TP53': 0.42,
                    'ALK': 0.36,
                },
            },
        }

        # Build the calc result.
        ctx = Context({
            'app': appCtx,
            'dataIn': dataIn,
            'layoutIndex': 0,
        })
        result = {
            'nodes': {
                'newNode1': {
                    'x': 73,
                    'y': 91,
                    'neighbors': {
                        'TCGA-BP-4790': 0.352,
                        'TCGA-AK-3458': 0.742,
                    }
                },
                'newNode2': {
                    'x': 53,
                    'y': 47,
                    'neighbors': {
                        'neighbor1': 0.567,
                        'neighbor2': 0.853,
                    }
                }
            }
        }
        status, result = placeNode_web._postCalc(result, ctx)
        #print 'result:', result
        data = result
        s.assertTrue('newNode1' in data['nodes'])
        s.assertTrue('newNode2' in data['nodes'])
        s.assertTrue('x' in data['nodes']['newNode1'])
        s.assertTrue(data['nodes']['newNode1']['x'] == 73)
        s.assertTrue('neighbors' in data['nodes']['newNode2'])
        s.assertTrue('TCGA-BP-4790' in data['nodes']['newNode1']['neighbors'])
        s.assertTrue(data['nodes']['newNode1']['neighbors']['TCGA-BP-4790'] == \
            0.352)
        bookmarkParm = '/?bookmark='
        sLen = len(s.viewServer) + len(bookmarkParm)
        s.assertTrue(data['nodes']['newNode1']['url'][:sLen] == \
            s.viewServer + bookmarkParm, data['nodes']['newNode1']['url'][
                                         :sLen] +
                     ' |didnt match| ' + s.viewServer + bookmarkParm)
        # urls for all nodes should be the same
        s.assertTrue(data['nodes']['newNode1']['url'] == \
            data['nodes']['newNode2']['url'])

    def test_multi_nodes_individual_urls_true(s):
   
        # Test that _postCalc() knows how to compose a bookmark from this data
        # returned from the calc routine.
        
        # Build the data input to the calc routine.
        dataIn = {
            'map': 'unitTest/layoutBasicExp',
            'layout': 'mRNA',
            'individualUrls': True,
            'nodes': {
                'newNode1': {
                    'TP53': 0.54,
                    'ALK': 0.32,
                },
                'newNode2': {
                    'TP53': 0.42,
                    'ALK': 0.36,
                },
            },
        }

        # Build the calc result.
        ctx = Context({
            'app': appCtx,
            'dataIn': dataIn,
            'layoutIndex': 0,
        })
        result = {
            'nodes': {
                'newNode1': {
                    'x': 73,
                    'y': 91,
                    'neighbors': {
                        'TCGA-BP-4790': 0.352,
                        'TCGA-AK-3458': 0.742,
                    }
                },
                'newNode2': {
                    'x': 53,
                    'y': 47,
                    'neighbors': {
                        'neighbor1': 0.567,
                        'neighbor2': 0.853,
                    }
                }
            }
        }
        status, result = placeNode_web._postCalc(result, ctx)
        #print 'result:', result
        data = result
        s.assertTrue('newNode1' in data['nodes'])
        s.assertTrue('newNode2' in data['nodes'])
        s.assertTrue('x' in data['nodes']['newNode1'])
        s.assertTrue(data['nodes']['newNode1']['x'] == 73)
        s.assertTrue('neighbors' in data['nodes']['newNode2'])
        s.assertTrue('TCGA-BP-4790' in data['nodes']['newNode1']['neighbors'])
        s.assertTrue(data['nodes']['newNode1']['neighbors']['TCGA-BP-4790'] == \
            0.352)
        bookmarkParm = '/?bookmark='
        sLen = len(s.viewServer) + len(bookmarkParm)
        s.assertTrue(data['nodes']['newNode1']['url'][:sLen] == \
            s.viewServer + bookmarkParm)
        # urls for all nodes should be differnet
        s.assertTrue(data['nodes']['newNode1']['url'] != \
            data['nodes']['newNode2']['url'])
    
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

if __name__ == '__main__':
    unittest.main()
