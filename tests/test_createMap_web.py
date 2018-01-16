import os, json, requests, re
import unittest
import testUtil
import testUtil as util
import www

class CreateMapTestCase(unittest.TestCase):

    # This view server must be running for these tests.
    viewServer = os.environ['VIEWER_URL']
    unprintable = '09'.decode('hex')  # tab character

    def setUp(self):
        www.app.config['UNIT_TEST'] = True
        self.app = www.app.test_client()

    def tearDown(self):
        pass
    
################ required parameter tests ######################

    def test_get_not_allowed(s):
        rv = s.app.get('/query/createMap')
        s.assertTrue(rv.status_code == 405)

    def test_content_type_not_json(s):
        rv = s.app.post('/query/createMap',
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
        rv = s.app.post('/query/createMap',
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
        rv = s.app.post('/query/createMap',
            content_type='application/json',
            data=json.dumps(dict(
                someData='someData',
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print 'rv.status_code:', rv.status_code
        s.assertTrue(rv.status_code == 400)
        #print "data['error']", data['error']
        s.assertTrue(data['error'] == 'map parameter missing or malformed')

    def test_bad_layoutInputDataId_string(s):
        rv = s.app.post('/query/createMap',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layoutInputDataId='x' + s.unprintable + 'x',
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print 'rv.status_code:', rv.status_code
        #print 'rv.data:', rv.data
        #print "data['error']", data['error']
        s.assertTrue(rv.status_code == 400)
        s.assertTrue(data['error'] ==
            'layoutInputDataId parameter should only contain printable characters')

    def test_bad_layoutInputDataId_filename(s):
        rv = s.app.post('/query/createMap',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layoutInputDataId='x#x',
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print 'rv.status_code:', rv.status_code
        #print 'rv.data:', rv.data
        #print "data['error']", data['error']
        s.assertTrue(rv.status_code == 400)
        msg = 'layoutInputDataId parameter may only contain the characters:' + \
            ' a-z, A-Z, 0-9, dash (-), dot (.), underscore (_), slash (/)'
        s.assertTrue(msg == data['error'])

    def test_bad_layoutInputName_string(s):
        rv = s.app.post('/query/createMap',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layoutInputDataId='x',
                layoutInputName='x' + s.unprintable + 'x',
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print 'rv.status_code:', rv.status_code
        s.assertTrue(rv.status_code == 400)
        #print "data['error']", data['error']
        s.assertTrue(data['error'] ==
            'layoutInputName parameter should only contain printable characters')

################  optional parameters tests ######################
    '''
    def test_bad_authGroup_string(s):
        rv = s.app.post('/query/createMap',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layoutInputDataId='x',
                layoutInputName='x',
                colorAttributeDataId='x',
                authGroup='x' + s.unprintable + 'x',
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print 'rv.status_code:', rv.status_code
        s.assertTrue(rv.status_code == 400)
        #print "data['error']", data['error']
        s.assertTrue(data['error'] ==
            'authGroup parameter should only contain printable characters')
    '''
    def test_neighborCount_not_integer(s):
        rv = s.app.post('/query/createMap',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layoutInputDataId='x',
                layoutInputName='x',
                colorAttributeDataId='x',
                neighborCount='x',
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print 'rv.status_code:', rv.status_code
        #print "data['error']", data['error']
        s.assertTrue(rv.status_code == 400)
        s.assertTrue(data['error'] ==
            'neighborCount parameter must be an integer')

    def test_neighborCount_not_valid_integer(s):
        rv = s.app.post('/query/createMap',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layoutInputDataId='x',
                layoutInputName='x',
                colorAttributeDataId='x',
                neighborCount=-1,
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print 'rv.status_code:', rv.status_code
        #s.assertTrue(rv.status_code == 400)
        #print "data['error']", data['error']
        s.assertTrue(data['error'] ==
            'neighborCount parameter must be within the range, 1-30')

    def test_bad_colorAttributeDataId_string(s):
        rv = s.app.post('/query/createMap',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layoutInputDataId='x',
                layoutInputName='x',
                colorAttributeDataId='x' + s.unprintable + 'x',
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print 'rv.status_code:', rv.status_code
        #print "data", str(data)
        #print "data['error']", data['error']
        s.assertTrue(rv.status_code == 400)
        s.assertTrue(data['error'] ==
            'colorAttributeDataId parameter should only contain printable characters')

    def test_bad_colorAttributeDataId_filename(s):
        rv = s.app.post('/query/createMap',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layoutInputDataId='x',
                layoutInputName='x',
                colorAttributeDataId='x#x',
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print 'rv.status_code:', rv.status_code
        s.assertTrue(rv.status_code == 400)
        #print "data['error']", data['error']
        msg = 'colorAttributeDataId parameter may only contain the characters:' + \
            ' a-z, A-Z, 0-9, dash (-), dot (.), underscore (_), slash (/)'
        s.assertTrue(msg == data['error'])
        
    ''' later, not on UI yet
    def test_bad_colormapDataId_string(s):
        rv = s.app.post('/query/createMap',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layoutInputDataId='x',
                layoutInputName='x',
                colormapDataId='x' + s.unprintable + 'x',
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print 'rv.status_code:', rv.status_code
        s.assertTrue(rv.status_code == 400)
        #print "data['error']", data['error']
        s.assertTrue(data['error'] ==
            'colormapDataId parameter should only contain printable characters')
    
    def test_bad_firstColorAttribute_string(s):
        rv = s.app.post('/query/createMap',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layoutInputDataId='x',
                layoutInputName='x',
                colorAttributeDataId='x',
                firstColorAttribute='x' + s.unprintable + 'x',
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print 'rv.status_code:', rv.status_code
        s.assertTrue(rv.status_code == 400)
        #print "data['error']", data['error']
        s.assertTrue(data['error'] ==
            'firstColorAttribute parameter should only contain printable characters')

    def test_layoutAwareStats_not_boolean(s):
        rv = s.app.post('/query/createMap',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layoutInputDataId='x',
                layoutInputName='x',
                colorAttributeDataId='x',
                layoutAwareStats=1,
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print 'rv.status_code:', rv.status_code
        s.assertTrue(rv.status_code == 400)
        #print "data['error']", data['error']
        s.assertTrue(data['error'] ==
            'layoutAwareStats parameter must be true or false')

    def test_layoutIndependentStats_not_boolean(s):
        rv = s.app.post('/query/createMap',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layoutInputDataId='x',
                layoutInputName='x',
                #colorAttributeDataId='x',
                layoutIndependentStats=1,
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print 'rv.status_code:', rv.status_code
        s.assertTrue(rv.status_code == 400)
        #print "data['error']", data['error']
        s.assertTrue(data['error'] ==
            'layoutIndependentStats parameter must be true or false')
    '''
    """
    # move to layout.py testing if we validate the colormap there.
    def test_good_colormap(s):
        rv = s.app.post('/query/createMap',
            content_type='application/json',
            data=json.dumps(dict(
                map='someMap',
                layoutInputDataId='x',
                layoutInputName='x',
                colorAttributeDataId='x',
                testColormaps=True,
                colormap=[
                   {
                       "attribute": "Disease",
                       "categories": [
                           "BRCA",
                           "LUAD",
                       ],
                       "colors": [
                          "#0000FF",
                          "#00FF00",
                       ]
                   },
                   {
                       "attribute": "Tumor Stage",
                       "categories": [
                           "Stage I",
                           "Stage II",
                       ],
                       "colors": [
                          "#0000FF",
                          "#00FF00",
                       ]
                   },
                ],
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print 'rv.status_code:', rv.status_code
        s.assertTrue(rv.status_code == 200)
        #print "data", data
        if data['Disease'][0]['name'] == 'BRCA' and \
            data['Disease'][0]['color'] == '#0000FF' and \
            data['Disease'][1]['name'] == 'LUAD' and \
            data['Disease'][1]['color'] == '#00FF00' and \
            data['Tumor Stage'][0]['name'] == 'Stage I' and \
            data['Tumor Stage'][0]['color'] == '#0000FF' and \
            data['Tumor Stage'][1]['name'] == 'Stage II' and \
            data['Tumor Stage'][1]['color']  == '#00FF00':
            s.assertTrue(True)
        else:
            s.assertTrue('actual' == 'expected')
    """
    '''
    # Negative tests for colormaps:
    
    def test_colormap_has_no_array_of_objects(s):

    def test_colormap_objects_without_attributes(s):

    def test_colormap_objects_without_categories(s):

    def test_colormap_objects_without_colors(s):

    def test_colormap_attributes_bad_string(s):

    def test_colormap_categories_bad_string(s):

    def test_colormap_colors_bad_string(s):

    def test_colormap_bad_attributes_count(s):

    def test_colormap_bad_categories_count(s):

    def test_colormap_bad_colors_count(s):

    '''
   



    '''
    def test_some_calc_error(s):
        rv = s.app.post('/query/createMap',
            content_type='application/json',
            data=json.dumps(dict(
                map='unitTest/layoutBasicExp',
                layout='mRNA',
                nodes = dict(
                    testError='something',
                ),
                testStub=True
            ))
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print "rv.status_code", rv.status_code
        #print "data['error']", data['error']
        s.assertTrue(rv.status_code == 400 or rv.status_code == 500)
        s.assertTrue(data['error'] == 'Some error message or stack trace')
    '''
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
