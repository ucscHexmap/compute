#!/usr/bin/env python2.7

import unittest, os, json, requests
from testUtil import message
from util_web import Context
import www
import viewData

appCtxDict = {
    'adminEmail': os.environ.get('ADMIN_EMAIL'),
    'dataRoot': 'in/dataRoot',
    'debug': os.environ.get('DEBUG', 0),
    'dev': int(os.environ.get('DEV', 0)),
    'hubPath': os.environ.get('HUB_PATH'),
    'unitTest': int(os.environ.get('UNIT_TEST', 0)),
    'viewServer': os.environ.get('VIEWER_URL', 'http://hexdev.sdsc.edu'),
}
appCtxDict['viewDir'] = os.path.join(appCtxDict['dataRoot'], 'view')
appCtxUnicode = json.loads(json.dumps(appCtxDict))
appCtx = Context(appCtxDict)

"""
def highlightAttrNode(data, appCtx):
data in: {
   "map": "CKCC/v1",
   "layout": "mRNA",
   "attributes": [
       "gender",
       "subType",
       ...
   ],
   "nodes": [
       "TCGA-01",
       "TCGA-02",
       ...
   ],
}
data out:
"""
class Test_highlightAttrNode(unittest.TestCase):


    def setUp(self):
        www.app.config['UNIT_TEST'] = True
        self.app = www.app.test_client()


    def tearDown(self):
        pass


    def test_post_no_attrs_no_nodes(s):
        rv = s.app.post('/highlightAttrNode',
            content_type='application/json',
            data=json.dumps({
                'map': 'unitTest/layoutBasicExp',
                'layout': 'layout'
            })
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print "data['error']", data['error']
        #print "data['stackTrace']:", data['stackTrace']
        s.assertTrue(rv.status_code == 400,
            'status code should be 400 but is ' + str(rv.status_code))
        s.assertTrue(data['error'] == 'One or both of the parameters, ' + \
            '"attributes" and "nodes" must be provided.')


    def test_post_no_attrs_with_nodes(s):
        rv = s.app.post('/highlightAttrNode',
            content_type='application/json',
            data=json.dumps({
                'map': 'unitTest/layoutBasicExp',
                'layout': 'layout',
                'nodes': [
                    'S1',
                    'S2'
                ]
            })
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print "data['error']", data['error']
        #print "data['stackTrace']:", data['stackTrace']
        s.assertTrue(rv.status_code == 200,
            'status code should be 200 but is ' + str(rv.status_code))


    def test_post_no_nodes_with_attrs(s):
        rv = s.app.post('/highlightAttrNode',
            content_type='application/json',
            data=json.dumps({
                'map': 'unitTest/layoutBasicExp',
                'layout': 'layout',
                'attributes': [
                    '3_categories',
                    'yes/No'
                ]
            })
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print "data['error']", data['error']
        #print "data['stackTrace']:", data['stackTrace']
        s.assertTrue(rv.status_code == 200,
            'status code should be 200 but is ' + str(rv.status_code))


    def test_post_good_data(s):
        rv = s.app.post('/highlightAttrNode',
            content_type='application/json',
            data=json.dumps({
                'map': 'unitTest/layoutBasicExp',
                'layout': 'layout',
                'attributes': [
                    '3_categories',
                    'yes/No'
                ],
                'nodes': [
                    'S1',
                    'S2'
                ]
            })
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print "data['error']", data['error']
        #print "data['stackTrace']:", data['stackTrace']
        s.assertTrue(rv.status_code == 200,
            'status code should be 200 but is ' + str(rv.status_code))


    def test_post_bookmark_generated(s):
        rv = s.app.post('/highlightAttrNode',
            content_type='application/json',
            data=json.dumps({
                'map': 'unitTest/layoutBasicExp',
                'layout': 'layout',
                'attributes': [
                    '3_categories',
                    'yes/No'
                ],
                'nodes': [
                    'S1',
                    'S2'
                ]
            })
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
        #print "data['error']", data['error']
        #print "data['stackTrace']:", data['stackTrace']
        #print "data:", data
        s.assertTrue(rv.status_code == 200,
            'status code should be 200 but is ' + str(rv.status_code))
        s.assertTrue('bookmark' in rv.data,
            'bookmark should be in response data but is not')
        expPrefix = appCtx.viewServer + '/?bookmark='
        expPrefixLen = len(expPrefix)
        actPrefix = data['bookmark'][:expPrefixLen]
        s.assertTrue(actPrefix == expPrefix,
            'URL prefix should be ' + expPrefix + ' but is ' + actPrefix)


    def test_good_full_data_state_generated(s):
        data = {
           'map': 'unitTest/layoutBasicExp',
            'layout': 'layout',
            'attributes': [
                '3_categories',
                'yes/No'
            ],
            'nodes': [
                'S1',
                'S2'
            ]
        }
        state = viewData._highlightAttrNodeInner(data, appCtx)
        #print "state", state
        s.assertTrue(state.keys() == ["project", "dynamicAttrs", "shortlist", "layoutName"],
            'state keys should be ["project", "layoutName", "shortlist", "dynamicAttrs"], but are ' + \
            str(state.keys()))
            
        s.assertTrue('project' in state,
            'project should be in the state, but is not')
        s.assertTrue(state['project'] == 'unitTest/layoutBasicExp',
            'project should be "unitTest/layoutBasicExp" but is ' + \
            state['project'])
            
        s.assertTrue('layoutName' in state,
            'layoutName should be in the state, but is not')
        s.assertTrue(state['layoutName'] == 'layout',
            'layoutName should be "layout" but is ' + state['layoutName'])
            
        s.assertTrue('shortlist' in state,
            'shortlist should be in the state, but is not')
        s.assertTrue(state['shortlist'] == ["yourNodes", "3_categories", "yes/No"],
            'shortlist should be ["yourNodes", "3_categories", "yes/No"] but is ' + \
            str(state['shortlist']))

        s.assertTrue('dynamicAttrs' in state,
            'dynamicAttrs should be in the state, but is not')
        s.assertTrue('yourNodes' in state["dynamicAttrs"],
            'yourNodes should be in state["dynamicAttrs"], but is not')
        s.assertTrue('dataType' in state['dynamicAttrs']['yourNodes'],
            'dataType should be in state["dynamicAttrs"]["yourNodes"], but is not')
        s.assertTrue('data' in state["dynamicAttrs"]["yourNodes"],
            'data should be in state["dynamicAttrs"]["yourNodes"], but is not')

        s.assertTrue(state["dynamicAttrs"]["yourNodes"]["dataType"] == "binary",
            'state["dynamicAttrs"]["yourNodes"]["dataType"] should be "binary", but is ' + \
            state["dynamicAttrs"]["yourNodes"]["dataType"])

        s.assertTrue('S1' in state["dynamicAttrs"]["yourNodes"]["data"],
            'S1 should be in state["dynamicAttrs"]["yourNodes"]["data"], but is not')
        s.assertTrue('S2' in state["dynamicAttrs"]["yourNodes"]["data"],
            'S2 should be in state["dynamicAttrs"]["yourNodes"]["data"], but is not')
            
        s.assertTrue(state["dynamicAttrs"]["yourNodes"]["data"]["S1"] == 1,
            'state["dynamicAttrs"]["yourNodes"]["data"]["S1"] should be 1, but is ' + \
            str(state["dynamicAttrs"]["yourNodes"]["data"]["S1"]))
        s.assertTrue(state["dynamicAttrs"]["yourNodes"]["data"]["S2"] == 1,
            'state["dynamicAttrs"]["yourNodes"]["data"]["S2"] should be 1, but is ' + \
            str(state["dynamicAttrs"]["yourNodes"]["data"]["S2"]))


    def test_good_map_nodes_state_generated(s):
        data = {
            'map': 'unitTest/layoutBasicExp',
            'nodes': [
                'S1',
                'S2'
            ]
        }
        state = viewData._highlightAttrNodeInner(data, appCtx)
        #print "state", state
        s.assertTrue(state.keys() == ["project", "dynamicAttrs", "shortlist"],
            'state keys should be ["project", "dynamicAttrs", "shortlist"], but are ' + \
            str(state.keys()))
            
        s.assertTrue('project' in state,
            'project should be in the state, but is not')
        s.assertTrue(state['project'] == 'unitTest/layoutBasicExp',
            'project should be "unitTest/layoutBasicExp" but is ' + \
            state['project'])
            
        s.assertTrue('shortlist' in state,
            'shortlist should be in the state, but is not')
        s.assertTrue(state['shortlist'] == ["yourNodes"],
            'shortlist should be ["yourNodes"] but is ' + \
            str(state['shortlist']))

        s.assertTrue('dynamicAttrs' in state,
            'dynamicAttrs should be in the state, but is not')
        s.assertTrue('yourNodes' in state["dynamicAttrs"],
            'yourNodes should be in state["dynamicAttrs"], but is not')
        s.assertTrue('dataType' in state['dynamicAttrs']['yourNodes'],
            'dataType should be in state["dynamicAttrs"]["yourNodes"], but is not')
        s.assertTrue('data' in state["dynamicAttrs"]["yourNodes"],
            'data should be in state["dynamicAttrs"]["yourNodes"], but is not')

        s.assertTrue(state["dynamicAttrs"]["yourNodes"]["dataType"] == "binary",
            'state["dynamicAttrs"]["yourNodes"]["dataType"] should be "binary", but is ' + \
            state["dynamicAttrs"]["yourNodes"]["dataType"])

        s.assertTrue('S1' in state["dynamicAttrs"]["yourNodes"]["data"],
            'S1 should be in state["dynamicAttrs"]["yourNodes"]["data"], but is not')
        s.assertTrue('S2' in state["dynamicAttrs"]["yourNodes"]["data"],
            'S2 should be in state["dynamicAttrs"]["yourNodes"]["data"], but is not')
            
        s.assertTrue(state["dynamicAttrs"]["yourNodes"]["data"]["S1"] == 1,
            'state["dynamicAttrs"]["yourNodes"]["data"]["S1"] should be 1, but is ' + \
            str(state["dynamicAttrs"]["yourNodes"]["data"]["S1"]))
        s.assertTrue(state["dynamicAttrs"]["yourNodes"]["data"]["S2"] == 1,
            'state["dynamicAttrs"]["yourNodes"]["data"]["S2"] should be 1, but is ' + \
            str(state["dynamicAttrs"]["yourNodes"]["data"]["S2"]))



    def test_good_map_attr_state_generated(s):
        data = {
           'map': 'unitTest/layoutBasicExp',
            'attributes': [
                '3_categories',
                'yes/No'
            ],
        }
        state = viewData._highlightAttrNodeInner(data, appCtx)
        #print "state", state
        s.assertTrue(state.keys() == ["project","shortlist"],
            'state keys should be ["project","shortlist"], but are ' + \
            str(state.keys()))
            
        s.assertTrue('project' in state,
            'project should be in the state, but is not')
        s.assertTrue(state['project'] == 'unitTest/layoutBasicExp',
            'project should be "unitTest/layoutBasicExp" but is ' + \
            state['project'])
            
        s.assertTrue('shortlist' in state,
            'shortlist should be in the state, but is not')
        s.assertTrue(state['shortlist'] == ["3_categories", "yes/No"],
            'shortlist should be ["3_categories", "yes/No"] but is ' + \
            str(state['shortlist']))

if __name__ == '__main__':
    unittest.main()
