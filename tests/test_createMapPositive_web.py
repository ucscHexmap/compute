
# Positive tests for createMap_web

import os, json, requests, re, shutil
from os import path
import unittest
import testUtil
import testUtil as util
import www, job

testDir = os.getcwd()
sourceDataDir = os.path.join(testDir , 'in/layout/')
dataRoot = os.path.join(testDir , 'out/createMapPositive_web')
expDirBase = os.path.join(testDir,'exp/layoutBasic')
expDir = expDirBase + '/'
expNoAttsDir = expDirBase+ 'NoAtts/'
expNoAtts2Dir = expDirBase+ 'NoAtts2/'
expNoColorDir = expDirBase + 'NoColor/'
expXyDir = expDirBase + 'Xy/'
expParmDir = expDirBase + 'Parm/'
expNoAttsLayoutParmsDir = expDirBase + 'noAttsParm/'

rawDataFile = os.path.join(inDir, 'full_matrix.tab')
rawDataFile_2 = os.path.join(inDir, 'full_matrix_2.tab')
fullSimDataFile = os.path.join(inDir, 'similarity_full.tab')
top6SimDataFile = os.path.join(inDir, 'similarity.tab')
coordDataFile = os.path.join(inDir,'coordinates.tab')
colorDataFile = os.path.join(inDir, 'colormaps.tab')

class CreateMapPositiveTestCase(unittest.TestCase):

    # This view server must be running for these tests.
    viewServer = os.environ['VIEWER_URL']
    unprintable = '09'.decode('hex')  # tab character

    def setUp(self):
        www.app.config['UNIT_TEST'] = True
        self.app = www.app.test_client()

    def tearDown(self):
        pass
    
    def setUpDirs (s, relativeDataRoot, map):
        
        # Set up directories in our standard data directory structure.
        myDataRoot = os.path.join(dataRoot, relativeDataRoot)

        # Clean up any old directories.
        try:
            shutil.rmtree(myDataRoot)
        except Exception as e:
            msg = 'unable to remove dataRoot: ' + myDataRoot + ' : ' + repr(e)
            s.assertTrue(msg, '')

        # Make the path for the feature data.
        featureRoot = path.join(myDataRoot, 'featureSpace')
        i = map.find('/')
        if i > -1:
            featureRoot = path.join(featureDir, map[0:i])
            target = map[i+1:]
        else:
            target = map
        os.makedirs(featureRoot)

        # Copy files from our usual layout input dir to
        # the map's featureSpace dir
        shutil.copytree(sourceDataDir, path.join(featureRoot, target))

        # Make some more paths
            data=json.dumps(dict(
                someData='someData',
            ))
        paths = dict(
            'out': path.join(myDataRoot, 'view', map),
            
            # Make full paths for the input data
            rawDataFile = os.path.join(inDir, 'full_matrix.tab')
            rawDataFile_2 = os.path.join(inDir, 'full_matrix_2.tab')
            fullSimDataFile = os.path.join(inDir, 'similarity_full.tab')
            top6SimDataFile = os.path.join(inDir, 'similarity.tab')
            coordDataFile = os.path.join(inDir,'coordinates.tab')
            colorDataFile = os.path.join(inDir, 'colormaps.tab')

        }
        os.makedirs(paths['out'])
        return paths

################  required parameter tests ######################
# following pattern in positive tests in test_layoutBasic.py

    def test_full_no_atts(s):
        relativeDataRoot = '_full_no_atts'
        map = 'major/minor'
        paths = s.setUpDirs(relativeDataRoot, map)
        rv = s.app.post('/query/createMap',
            content_type='application/json',
            data=json.dumps({
                "map": map,
                "layoutInputDataId": fullSimDataFile,
                "layoutInputName": "layout",
            })
        )
        try:
            data = json.loads(rv.data)
        except:
            s.assertTrue('', 'no json data in response')
    
        print 'rv.status_code:', rv.status_code
        print 'rv:', rv
        #s.assertTrue(rv.status_code == 200)
        print 'data', data
        s.assertTrue(data['status'] == 'Request received')
        s.assertTrue(data['jobId'] == '1111')
            
        # poll for completion
        # util.compareActualVsExpectedDir(s, expNoAttsDir, outDir)




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
