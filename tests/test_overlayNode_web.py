import os, json, requests
import unittest
import testUtil
from testUtil import message
import www

class Test_overlayNode(unittest.TestCase):

    # This view server must be running for these tests.
    viewServer = os.environ['VIEWER_URL']
    unprintable = '09'.decode('hex')  # tab character

    def setUp(self):
        www.app.config['UNIT_TEST'] = True
        self.app = www.app.test_client()

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
                email=['someone@somewhere'],
                viewServer=s.viewServer,
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
    
    def test_map_has_background_data(s):
        rv = s.app.post('/query/overlayNodes',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layout='someLayout',
                nodes=dict(
                    someNode='someValue',
                )
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print "### rv.status_code:", rv.status_code
        #print "### data['error']:", data['error']
        expected = """Server uncaught exception: Clustering data not found for layout: someLayout"""

        s.assertTrue(
            rv.status_code == 500,
            data
            #message(rv.status_code, 500)
        )
        s.assertTrue(
            data['error'] == expected,
            data['stackTrace']
            #message(data['error'], expected)
        )

    def test_layout_has_background_data(s):
        rv = s.app.post('/query/overlayNodes',
            content_type='application/json',
            data=json.dumps(dict(
                map='unitTest/layoutBasicExp',
                layout='someLayout',
                nodes = dict(
                    someNode='someValue',
                ),
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')

        #print "rv.status_code", rv.status_code
        #print "data['error']", data['error']
        expectedResult = \
            'Clustering data not found for layout: someLayout'
        s.assertTrue(
            rv.status_code == 500,
            message(rv.status_code, 500)
        )
        expectedMessage = """Server uncaught exception: Clustering data not found for layout: someLayout"""

        s.assertTrue(
            data['error'] == expectedMessage,
            message(data['error'], expectedMessage)
        )

    def test_create_bookmark(s):
        #resData = '{"TESTpythonCallStub":"success"}\n';
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
        #print "rc['data']:", rc['data']
        s.assertTrue(rc['code'] == '200')
    
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
