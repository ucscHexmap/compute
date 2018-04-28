

import os, json
import unittest
import www
import projectList
from util_web import Context, ErrorResp
from validate_web import cleanFileName

testRoot = os.getcwd()
dataRoot = os.path.join(testRoot, 'in/project')
email = 'user@ucsc.edu'
userDir = 'user_ucsc.edu'

appCtxDict = {
    'dev': int(os.environ.get('DEV', 0)),
    'dataRoot': dataRoot,
    'unitTest': True,
    'dataRoot': os.path.join(dataRoot, 'viewBasic'),
    'viewServer': os.environ['VIEWER_URL'],
}
appCtx = Context(appCtxDict)
url = os.environ['WWW_SOCKET']
if os.environ['USE_HTTPS'] == '1':
    appCtx.dataServer = 'https://' + url
else:
    appCtx.dataServer = 'http://' + url

class Test_projectList(unittest.TestCase):

    def setUp(self):
        self.app = www.app.test_client()
        www.appCtx.dataRoot = dataRoot

    def tearDown(self):
        pass

    def test_getSubDirs(s):
        viewRoot = os.path.join(dataRoot, 'viewBasic')
        subDirs = projectList._getSubDirs(viewRoot)
        s.assertTrue(subDirs == ['major1', 'major2', 'major3', userDir],
            'subDirs: ' + str(subDirs))
    
    def test_getProjectRoles (s):
        viewRoot = os.path.join(dataRoot, 'viewBasic')
        roles = projectList._getProjectRoles('major1', viewRoot)
        s.assertTrue(roles == ['public'], 'roles: ' + str(roles))
    
    def test_getProjectRolesTwo (s):
        viewRoot = os.path.join(dataRoot, 'viewBasic')
        roles = projectList._getProjectRoles('major2', viewRoot)
        s.assertTrue(roles == ['mine', 'yours'], 'roles: ' + str(roles))
    
    def test_getProjectRolesNone (s):
        viewRoot = os.path.join(dataRoot, 'viewBasic')
        roles = projectList._getProjectRoles('major3', viewRoot)
        s.assertTrue(roles == [], 'roles: ' + str(roles))
    
    def test_getProjectRolesBadJson (s):
        viewRoot = os.path.join(dataRoot, 'viewProjRole')
        try:
            roles = projectList._getProjectRoles('major1', viewRoot)
        except ErrorResp:
            s.assertTrue(1 == 1)
            return
        s.assertTrue('bad json not caught' == 1, 'errorResp: ' + errorResp)

    def test_getProjectRolesNoneWithJson (s):
        viewRoot = os.path.join(dataRoot, 'viewProjRole')
        try:
            roles = projectList._getProjectRoles('major2', viewRoot)
        except ErrorResp:
            s.assertTrue(1 == 1)
            return
        s.assertTrue('bad json not caught' == 1, 'errorResp: ' + errorResp)

    def test_isUserInRoleOneToOne (s):
        viewRoot = os.path.join(dataRoot, 'viewUserInRole')
        userInRole = projectList._isUserInRole( ['thisProjRole'], ['thisProjRole'])
        s.assertTrue(userInRole)

    def test_isUserInRoleOneToOneNot (s):
        viewRoot = os.path.join(dataRoot, 'viewUserInRole')
        userInRole = projectList._isUserInRole( ['anotherRole'], ['thisProjRole'])
        s.assertTrue(userInRole == False)

    def test_isUserInRoleOneToMany (s):
        viewRoot = os.path.join(dataRoot, 'viewUserInRole')
        userInRole = projectList._isUserInRole( ['anotherRole'], ['thisProjRole', 'anotherRole'])
        s.assertTrue(userInRole)

    def test_isUserInRoleOneToManyNot (s):
        viewRoot = os.path.join(dataRoot, 'viewUserInRole')
        userInRole = projectList._isUserInRole( ['userRole'], ['thisProjRole', 'anotherRole'])
        s.assertTrue(userInRole == False)

    def test_isUserInRoleManyToMany (s):
        viewRoot = os.path.join(dataRoot, 'viewUserInRole')
        userInRole = projectList._isUserInRole( ['userRole', 'anotherRole'], ['thisProjRole', 'anotherRole'])
        s.assertTrue(userInRole)

    def test_isUserInRoleManyToManyNot (s):
        viewRoot = os.path.join(dataRoot, 'viewUserInRole')
        userInRole = projectList._isUserInRole( ['userRole', 'anotherUserRole'], ['thisProjRole', 'anotherRole'])
        s.assertTrue(userInRole == False)

    def test_cleanFileName (s):
        clean = cleanFileName('user@/=$')
        s.assertTrue(clean == 'user____', 'clean string is ' + clean)
    
    def test_rolesToList_list (s):
        roles = ['nuts', 'peanuts']
        lst = projectList._rolesToList(roles)
        s.assertTrue(lst == ['nuts', 'peanuts'], 'lst: ' + str(lst))

    def test_rolesToList_string (s):
        roles = 'nuts'
        lst = projectList._rolesToList(roles)
        s.assertTrue(lst == ['nuts'], 'lst: ' + str(lst))

    def test_rolesToList_emptyList (s):
        roles = []
        lst = projectList._rolesToList(roles)
        s.assertTrue(lst == [], 'lst: ' + str(lst))

    def test_rolesToList_None (s):
        roles = None
        lst = projectList._rolesToList(roles)
        s.assertTrue(lst == [], 'lst: ' + str(lst))

    def test_isUserAuthorizedPublic (s):
        userAuthd = projectList._isUserAuthorized(
            userEmail=email,
            userRole=[],
            major='major1',
            projRole=['public']
        )
        s.assertTrue(userAuthd, 'userAuthd: ' + str(userAuthd))

    def test_isUserAuthorizedNoUser (s):
        userAuthd = projectList._isUserAuthorized(
            userEmail=None,
            userRole=[],
            major='major1',
            projRole=['nuts']
        )
        s.assertTrue(userAuthd == False, 'userAuthd: ' + str(userAuthd))

    def test_isUserAuthorizedUserProject (s):
        userAuthd = projectList._isUserAuthorized(
            userEmail=email,
            userRole=[],
            major=userDir,
            projRole=[]
        )
        s.assertTrue(userAuthd, 'userAuthd: ' + str(userAuthd))

    def test_isUserAuthorizedUserProject (s):
        userAuthd = projectList._isUserAuthorized(
            userEmail=email,
            userRole=[],
            major=userDir,
            projRole=[]
        )
        s.assertTrue(userAuthd, 'userAuthd: ' + str(userAuthd))

    def test_isUserAuthorizedNoUserRoles (s):
        userAuthd = projectList._isUserAuthorized(
            userEmail=email,
            userRole=[],
            major='major1',
            projRole=['nuts']
        )
        s.assertTrue(userAuthd == False, 'userAuthd: ' + str(userAuthd))

    def test_isUserAuthorizedDevAccess (s):
        userAuthd = projectList._isUserAuthorized(
            userEmail=email,
            userRole=['dev'],
            major='major1',
            projRole=['nuts']
        )
        s.assertTrue(userAuthd, 'userAuthd: ' + str(userAuthd))

    def test_isUserAuthorizedWithRoleMatch (s):
        userAuthd = projectList._isUserAuthorized(
            userEmail=email,
            userRole=['nuts'],
            major='major1',
            projRole=['nuts']
        )
        s.assertTrue(userAuthd, 'userAuthd: ' + str(userAuthd))

    def test_isUserAuthorizedNoRoleMatch (s):
        userAuthd = projectList._isUserAuthorized(
            userEmail=email,
            userRole=['peanuts'],
            major='major1',
            projRole=['nuts']
        )
        s.assertTrue(userAuthd == False, 'userAuthd: ' + str(userAuthd))
    
    def test_removeNonAuthdDirs (s):
        viewRoot = os.path.join(dataRoot, 'viewBasic')
        lst = projectList._removeNonAuthdDirs (
            majors = ['major1', 'major2', 'major3', userDir],
            userEmail  = email,
            userRoles = ['mine'],
            viewDir = viewRoot
        )
        s.assertTrue(lst == ['major1', 'major2', userDir], 'lst: ' + str(lst))

    def test_removeNonAuthdDirs_NoneLeft (s):
        viewRoot = os.path.join(dataRoot, 'viewRemoveNonAuthdDirs')
        lst = projectList._removeNonAuthdDirs (
            majors = ['major1', 'major2'],
            userEmail  = email,
            userRoles = ['mine'],
            viewDir = viewRoot
        )
        s.assertTrue(lst == [], 'lst: ' + str(lst))

    def test_addMinors (s):
        viewRoot = os.path.join(dataRoot, 'viewBasic')
        projs = projectList._addMinors (
            majors = ['major1', 'major2', 'major3', userDir],
            viewDir = viewRoot
        )
        #print 'userDir:', userDir
        s.assertTrue(projs == [
            ['major1', ['major1a', 'major1b']],
            ['major2', ['major2a', 'major2b']],
            ['major3'],
            [userDir]
            ], 'projs: ' + str(projs))

    def test_addMinors_noMajors (s):
        viewRoot = os.path.join(dataRoot, 'viewBasic')
        projs = projectList._addMinors (
            majors = [],
            viewDir = viewRoot
        )
        s.assertTrue(projs ==[], 'projs: ' + str(projs))

    def test_get (s):
        viewRoot = os.path.join(dataRoot, 'viewBasic')
        dict = projectList.get(
            userEmail = email,
            userRoles = ['mine'],
            viewDir = os.path.join(dataRoot, 'viewBasic')
        )
        dictJson = json.dumps(dict, sort_keys=True)
        expected = [
            ['major1', ['major1a', 'major1b']],
            ['major2', ['major2a', 'major2b']],
            [userDir]
        ]
        expectedJson = json.dumps(expected, sort_keys=True)
        #print 'expectedJson:', expectedJson
        s.assertTrue(expectedJson == dictJson, 'dictJson: ' + str(dictJson))
    
    def test_auth_route (s):
        www.appCtx.viewDir = os.path.join(www.appCtx.dataRoot, 'viewBasic')
        try:
            r = s.app.get('/mapAuth/mapId/major1/major1a/email/user@ucsc.edu/role/mine')
        except:
            s.assertEqual('', 'Unable to connect to unit test data server: ' +
                appCtx.dataServer)
        #print 'r.status_code:', str(r.status_code)
        s.assertTrue(r.status_code == 200, 'r.status_code: ' + str(r.status_code))
        expected = { 'authorized': True }
        dataDict = json.loads(r.data)
        #print 'dataDict:', dataDict
        s.assertTrue(expected == dataDict, 'dataDict: ' + str(dataDict))
    
    def test_auth_route_multiUserRoles (s):
        www.appCtx.viewDir = os.path.join(www.appCtx.dataRoot, 'viewBasic')
        try:
            r = s.app.get('/mapAuth/mapId/major1/major1a/email/user@ucsc.edu/role/mine+dev')
        except:
            s.assertEqual('', 'Unable to connect to unit test data server: ' +
                appCtx.dataServer)
        #print 'r.status_code:', str(r.status_code)
        s.assertTrue(r.status_code == 200, 'r.status_code: ' + str(r.status_code))
        expected = { 'authorized': True }
        dataDict = json.loads(r.data)
        #print 'dataDict:', dataDict
        s.assertTrue(expected == dataDict, 'dataDict: ' + str(dataDict))
    
    def test_auth_route_noUserRolesNorKeyword (s):
        www.appCtx.viewDir = os.path.join(www.appCtx.dataRoot, 'viewBasic')
        try:
            r = s.app.get('/mapAuth/mapId/major1/major1a/email/user@ucsc.edu')
        except:
            s.assertEqual('', 'Unable to connect to unit test data server: ' +
                appCtx.dataServer)
        #print 'r.status_code:', str(r.status_code)
        s.assertTrue(r.status_code == 200, 'r.status_code: ' + str(r.status_code))
        expected = { 'authorized': True }
        dataDict = json.loads(r.data)
        #print 'dataDict:', dataDict
        s.assertTrue(expected == dataDict, 'dataDict: ' + str(dataDict))
    
    def test_auth_route_noEmailNorKeyword (s):
        www.appCtx.viewDir = os.path.join(www.appCtx.dataRoot, 'viewBasic')
        try:
            r = s.app.get('/mapAuth/mapId/major1/major1a')
        except:
            s.assertEqual('', 'Unable to connect to unit test data server: ' +
                appCtx.dataServer)
        #print 'r.status_code:', str(r.status_code)
        s.assertTrue(r.status_code == 200, 'r.status_code: ' + str(r.status_code))
        expected = { 'authorized': True }
        dataDict = json.loads(r.data)
        #print 'dataDict:', dataDict
        s.assertTrue(expected == dataDict, 'dataDict: ' + str(dataDict))
    
    def test_auth_route_noProject (s):
        www.appCtx.viewDir = os.path.join(www.appCtx.dataRoot, 'viewBasic')
        try:
            r = s.app.get('/mapAuth/mapId')
        except:
            s.assertEqual('', 'Unable to connect to unit test data server: ' +
                appCtx.dataServer)
        #print 'r.status_code:', str(r.status_code)
        s.assertTrue(r.status_code == 404, 'r.status_code: ' + str(r.status_code))

    def test_auth_route_badProject (s):
        www.appCtx.viewDir = os.path.join(www.appCtx.dataRoot, 'viewBasic')
        try:
            r = s.app.get('/mapAuth/mapId/badProject')
        except:
            s.assertEqual('', 'Unable to connect to unit test data server: ' +
                appCtx.dataServer)
        #print 'r.status_code:', str(r.status_code)
        s.assertTrue(r.status_code == 200, 'r.status_code: ' + str(r.status_code))
        expected = { 'authorized': False }
        dataDict = json.loads(r.data)
        #print 'dataDict:', dataDict
        s.assertTrue(expected == dataDict, 'dataDict: ' + str(dataDict))

    def test_route (s):
        www.appCtx.viewDir = os.path.join(www.appCtx.dataRoot, 'viewBasic')
        try:
            r = s.app.get('/mapList/email/user@ucsc.edu/role/mine')
        except:
            s.assertEqual('', 'Unable to connect to unit test data server: ' +
                appCtx.dataServer)
        s.assertTrue(r.status_code == 200, 'r.status_code: ' + str(r.status_code))
        expected = [
            ['major1', ['major1a', 'major1b']],
            ['major2', ['major2a', 'major2b']],
            [userDir]
        ]
        dataDict = json.loads(r.data)
        #print 'dataDict:', dataDict
        s.assertTrue(expected == dataDict, 'dataDict: ' + str(dataDict))
    
    def test_route_multiRoles (s):
        www.appCtx.viewDir = os.path.join(www.appCtx.dataRoot, 'viewBasic')
        try:
            r = s.app.get('/mapList/email/user@ucsc.edu/role/mine+dev')
        except:
            s.assertEqual('', 'Unable to connect to unit test data server: ' +
                appCtx.dataServer)
        s.assertTrue(r.status_code == 200, 'r.status_code: ' + str(r.status_code))
        expected = [
            ['major1', ['major1a', 'major1b']],
            ['major2', ['major2a', 'major2b']],
            ['major3'],
            [userDir]
        ]
        dataDict = json.loads(r.data)
        s.assertTrue(expected == dataDict, 'dataDict: ' + str(dataDict))

    def test_route_noRolesNorKeyword (s):
        www.appCtx.viewDir = os.path.join(www.appCtx.dataRoot, 'viewBasic')
        try:
            r = s.app.get('/mapList/email/user@ucsc.edu')
        except:
            s.assertEqual('', 'Unable to connect to unit test data server: ' +
                appCtx.dataServer)
        s.assertTrue(r.status_code == 200, 'r.status_code: ' + str(r.status_code))
        expected = [
            ['major1', ['major1a', 'major1b']],
            [userDir]
        ]
        dataDict = json.loads(r.data)
        s.assertTrue(expected == dataDict, 'dataDict: ' + str(dataDict))

    def test_route_noEmailNorKeyword (s):
        www.appCtx.viewDir = os.path.join(www.appCtx.dataRoot, 'viewBasic')
        try:
            r = s.app.get('/mapList')
        except:
            s.assertEqual('', 'Unable to connect to unit test data server: ' +
                appCtx.dataServer)
        s.assertTrue(r.status_code == 200, 'r.status_code: ' + str(r.status_code))
        expected = [
            ['major1', ['major1a', 'major1b']]
        ]
        dataDict = json.loads(r.data)
        s.assertTrue(expected == dataDict, 'dataDict: ' + str(dataDict))

if __name__ == '__main__':
    unittest.main()
