
# Main module for the http server, including all routes.

import os, traceback, logging, json
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

import createMap_web
import job
import jobTestHelper_web
import placeNode_web
import projectEdit
import projectList
import reflect_web
import statsNoLayout_web
import statsLayout_web
import viewData

from util_web import SuccessResp, SuccessRespNoJson, ErrorResp, Context, \
    reportRouteError, getAppCtx
import validate_web as validate

# Set up the flask application.
app = Flask(__name__)

# Set up the application context used by all threads.
def contextInit ():
    global appCtx
    appCtx = getAppCtx()
    appCtx.adminEmail = os.environ.get('ADMIN_EMAIL')
    appCtx.dataRoot = os.environ.get('DATA_ROOT', 'DATA_ROOT_ENV_VAR_MISSING')
    appCtx.debug = os.environ.get('DEBUG', 0)
    appCtx.dev = int(os.environ.get('DEV', 0))
    appCtx.hubPath = os.environ.get('HEXCALC')
    appCtx.unitTest = int(os.environ.get('UNIT_TEST', 0))
    appCtx.viewServer = os.environ.get('VIEWER_URL', 'https://tumormap.ucsc.edu')
    appCtx.viewServerAddrs = os.environ.get('VIEW_SERVER_ADDRS', '127.0.0.1')

    # Derived context.
    appCtx.databasePath = \
        os.environ.get('DATABASE_PATH', appCtx.hubPath + '/../computeDb')
    appCtx.jobQueuePath = os.path.abspath(
        os.path.join(appCtx.databasePath, 'jobQueue.db'))
    appCtx.jobProcessPath = appCtx.hubPath + '/www/job/jobProcess.py'
    appCtx.viewDir = os.path.join(appCtx.dataRoot, 'view')
    url = os.environ['DATA_HOST_PORT']
    #url = os.environ['WWW_SOCKET']

    if os.environ['USE_HTTPS'] == '1':
        appCtx.dataServer = 'https://' + url
    else:
        appCtx.dataServer = 'http://' + url
    appCtx.jobStatusUrl = appCtx.dataServer + '/jobStatus/jobId/'
    return appCtx


def blueprintInit ():
    if not appCtx.unitTest:
        from www.upload.uploadRoutes import uploadRoutes
        app.register_blueprint(uploadRoutes)


# Set up logging
def loggingInit ():
    logFormat = '%(asctime)s %(levelname)s: %(message)s'
    logLevel = None
    if appCtx.unitTest:

        # Use critical level to disable all messages so unit tests only output
        # unit test errors.
        logging.basicConfig(level=logging.CRITICAL, format=logFormat)
        logLevel = 'CRITICAL'
    elif appCtx.debug:
        logging.basicConfig(level=logging.DEBUG, format=logFormat)
        logLevel = 'DEBUG'
    else:
        logging.basicConfig(level=logging.INFO, format=logFormat)
        logLevel = 'INFO'

    logging.info('WWW server started with log level: ' + logLevel)


# Initialize the app.
def initialize():

    # Make cross-origin AJAX possible
    CORS(app)
    
    contextInit()
    blueprintInit()
    loggingInit()

    # Create the database path if it does not exist.
    try:
        os.makedirs(appCtx.databasePath)
    except:
        pass


# Validate a post
def validatePost():
    if request.headers['Content-Type'] != 'application/json':
        raise ErrorResp('Content-Type must be application/json')
    try:
        dataIn = request.get_json()
    except:
        raise ErrorResp('Post content is invalid JSON')

    # Validate an optional email address so we know who a job belongs to.
    validate.email(dataIn)

    return dataIn


# Convert a string with '+' as delimters into a list.
def _urlParmToList (value):
    if type(value) == list:
        return value
    else:
        return value.split('+')


# Register the success handler to convert to json
@app.errorhandler(SuccessResp)
def successResponse(success):
    response = jsonify(success.data)
    response.status_code = 200
    #logging.info('success json response: ' + str(response))
    return response


# Register the success handler that doesn't convert to json
@app.errorhandler(SuccessRespNoJson)
def successResponseNoJson(success):
    response = success.data
    response.status_code = 200
    #logging.info('success no json response: ' + str(response))
    return response


# Register the error handler
@app.errorhandler(ErrorResp)
def errorResponse(error):
    response = jsonify(error.message)
    response.status_code = error.status_code
    #statusCode, responseStr = str(response.status_code), str(response)
    return response


# Register the unhandled Exception handler
@app.errorhandler(Exception)
def unhandledException(e):
    trace = traceback.format_exc(100)
    # Build response.
    rdict = {
            "stackTrace" : trace,
            "error" : 'Server uncaught exception: ' + str(e),
            }
    response = jsonify(rdict)
    response.status_code = 500
    reportRouteError(response.status_code, rdict['error'], appCtx,
        rdict['stackTrace'])
    return response


def dataRouteInner(dataId, ok404=False):

    # Not using flask's send_file() as it mangles files larger than 32k.
    # Not using flask's GET because we need to capture 404-file-not-found
    # errors in the case that is ok with the client and return success.
    try:
        with open(os.path.join(appCtx.dataRoot, dataId)) as f:
            data = f.read()
            result = Response(
                data,
                mimetype='text/csv',
                headers={'Content-disposition': 'attachment'})
    except IOError:
        if ok404:
            result = Response(
                '404',
                mimetype='text/csv',
                headers={'Content-disposition': 'attachment'})
            raise SuccessRespNoJson(result)
        else:
            raise ErrorResp('File not found or other IOError', 404)

    raise SuccessRespNoJson(result)

# Handle data/<dataId> routes which are data requests by data ID.
@app.route('/data/<path:dataId>', methods=['GET'])
def dataRoute(dataId):
    dataRouteInner(dataId)


# Handle data404ok/<dataId> routes which are data requests by data ID.
# A 404 is ok to return here, so we do it as 'success' so that errors
# will not be thrown on the client console.
# TODO: the data server should be returning a 204 rather than 404.
#       error 204 would not make an http error display on the browser console
#       and would make this logic more simple.
@app.route('/dataOk404/<path:dataId>', methods=['GET'])
def dataRouteOk404(dataId):
    dataRouteInner(dataId, True)


# Handle route to delete a map.
@app.route('/deleteMap/mapId/<path:mapId>/email/<string:userEmail>',
    methods=['GET'])
@app.route('/deleteMap/mapId/<path:mapId>' + \
    '/email/<string:userEmail>/role/<string:userRole>', methods=['GET'])
def deleteMap(mapId, userEmail=None, userRole=[]):

    # Verify this is from the allowed view server
    if not request.environ['REMOTE_ADDR'] in appCtx.viewServerAddrs:
        raise ErrorResp('', 404)
    
    raise SuccessResp(
        projectEdit.delete(mapId, userEmail, _urlParmToList(userRole), appCtx))


# Handle route: get attribute names by map ID.
@app.route('/attrList/mapId/<path:mapId>', methods=['GET'])
def getAttrListRoute(mapId):
    raise SuccessResp(viewData.getAttrList(mapId, appCtx))


# Handle route: get layout names by map ID.
@app.route('/layoutList/mapId/<path:mapId>', methods=['GET'])
def getLayoutListRoute(mapId):
    raise SuccessResp(viewData.getLayoutList(mapId, appCtx))


# Get default first attribute name.
@app.route('/firstAttr/mapId/<path:mapId>', methods=['GET'])
# attrId is defined as a path in case it contains a slash.
def getFirstAttr(mapId):
    raise SuccessResp(viewData.getFirstAttr(mapId, appCtx))


# Handle get attr by ID (name, not index) and map.
@app.route('/attr/attrId/<path:attrId>/mapId/<path:mapId>', methods=['GET'])
# attrId is defined as a path in case it contains a slash.
def getAttrById(attrId, mapId):
    raise SuccessResp(viewData.getAttrById(attrId, mapId, appCtx))


# Handle get all jobs route
@app.route('/getAllJobs', methods=['GET'])
def getAllJobsRoute():
    raise SuccessResp(job.getAll(appCtx.jobQueuePath))


# Handle map authorization routes
@app.route('/mapAuth/mapId/<path:mapId>', methods=['GET'])
@app.route('/mapAuth/mapId/<path:mapId>/email/<string:userEmail>', \
    methods=['GET'])
@app.route('/mapAuth/mapId/<path:mapId>' + \
    '/email/<string:userEmail>/role/<string:userRole>', methods=['GET'])
def mapAuthRoute(mapId, userEmail=None, userRole=[]):
    raise SuccessResp(projectList.authorize(mapId, userEmail,
        _urlParmToList(userRole), appCtx.viewDir))


# Handle get map list routes
@app.route('/mapList', methods=['GET'])
@app.route('/mapList/email/<string:userEmail>', methods=['GET'])
@app.route('/mapList/email/<string:userEmail>/role/<string:userRole>',
    methods=['GET'])
def getMapListRoute(userEmail=None, userRole=[]):
    raise SuccessResp(
        projectList.get(userEmail, _urlParmToList(userRole), appCtx.viewDir))
    

# Handle jobStatus route
@app.route('/jobStatus/jobId/<int:jobId>', methods=['GET'])
def jobStatusRoute(jobId):
    raise SuccessResp(job.getStatus(jobId, appCtx.jobQueuePath))


# Handle route to save a portion of a colormap.
@app.route('/updateColor', methods=['POST'])
def updateColor():

    # Verify this is from the allowed view server.
    # TODO why not use the view server name and certificate here,
    # rather than the IP addr?
    if not request.environ['REMOTE_ADDR'] in appCtx.viewServerAddrs:
        raise ErrorResp('', 404)
    
    raise SuccessResp(projectEdit.updateColor(validatePost(), appCtx))


# Handle highlight attrs & nodes route
@app.route('/highlightAttrNode', methods=['POST'])
def highlightAttrNodeRoute():
    raise SuccessResp(viewData.highlightAttrNode(validatePost(), appCtx))


# Handle jobTestHelper route.
@app.route('/query/jobTestHelper', methods=['POST'])
def queryJobTestHelperRoute():
    raise SuccessResp(
        jobTestHelper_web.preCalc(validatePost(), Context({'app': appCtx})))


# Handle createMap route.
@app.route('/query/createMap', methods=['POST'])
def queryCreateMapRoute():
    raise SuccessResp(
        createMap_web.preCalc(validatePost(), Context({'app': appCtx })))


# Handle overlayNode route, older version of placeNode
@app.route('/query/overlayNodes', methods=['POST'])
def queryOverlayNodesRoute():
    raise SuccessResp(placeNode_web.preCalc(validatePost(),
        Context({'app': appCtx, 'overlayNodes': True})))


# Handle placeNode routes
@app.route('/query/placeNode', methods=['POST'])
def queryPlaceNodeRoute():
    raise SuccessResp(
        placeNode_web.preCalc(validatePost(), Context({'app': appCtx})))


# Handle one-by-all layout-independent stats routes.
@app.route('/oneByAll/statCalculation', methods=['POST'])
def oneByAllStatRequest():
    """
    Post example:
    {
        map : "PancanAtlas/SampleMap",
        focusAttr: opts.dynamicData,
        focusAttrDatatype : dType,
        email : Meteor.user().username,
    };
    focusAttr is in this form:
        {"attrName" : { "sampleId" : value}, ... }
    focus attribute datatype is one of:
        ["bin", "cat", "cont"]

    JSON response on Success from job queue:
        {result:
            [
                [ attributeId, single-test pvalue, BHFDR, bonefonni],
                ...,
                ...
            ]
        }
        For all attributes on the requested map.
    """
    logging.info('One By All Stat requested')

    parms = validatePost()
    ctx = Context({'app': appCtx})

    responseDict = statsNoLayout_web.preCalc(parms, ctx)
    logging.info(responseDict)

    raise SuccessResp(responseDict)


# Handle one-by-all layout-aware stats route.
@app.route('/oneByAll/leesLCalculation', methods=['POST'])
def oneByAllLeesLRequest():
    """
    Post example:
    {
        map : "PancanAtlas/SampleMap",
        focusAttr: opts.dynamicData,
        layoutIndex : 1,
        email : Meteor.user().username,
    };
    focusAttr is in this form:
        {"attrName" : { "sampleId" : value}, ... }

    JSON response on Success from job queue:
        {result:
            [
                [ attributeId, leesL, Rank, Pearson],
                ...,
                ...
            ]
        }
        For all attributes on the requested map.
    """
    logging.info('One By All LeesL requested')

    parms = validatePost()
    ctx = Context({'app': appCtx})

    responseDict = statsLayout_web.preCalc(parms, ctx)
    logging.info(responseDict)

    raise SuccessResp(responseDict)


# Handle reflect metadata route.
@app.route('/reflect/metaData/mapId/<path:mapId>', methods=['GET'])
def getReflectMetadata(mapId):
    """
    :returns:
     {
        toMapIds : []
        dataType : []
    }
    """
    responseDict = reflect_web.getReflectionMetadata(mapId)
    raise SuccessResp(responseDict)


# Handle reflect computation route.
@app.route('/reflect', methods=['POST'])
def reflectionRequest():
    """
    JSON post example
    {
        dataType : "dataTypePointsToAFileInReflectionConfig"
        layout : "layoutTheToMapWillOpenUpOn"
        toMap : "mapToViewReflection"
        map : "Pancan12/SampleMap",
        nodeIds : [id, id, ...],
        rankCategories: True/False,
        dynamicAttrName : "Kindey Isle"
        email: dmccoll@ucsc.edu
    };
    JSON response on Success from job queue:
        {
            url : "http://aLong/UrlForTheClient/ToViewReflectionOnAMap"
            dataRetrievalUrl : HUB_URL/reflect/attrId/<string:fileId>,
            nNodes : 123
        }
        dataRetrievalUrl is an enpoint to download the calculated file.
        "url" will open a map viewer with the reflection in your
        browser.
        nNodes is the number of nodes there was data for when
        calculating reflection.
    """
    logging.info('Reflection requested')

    parms = validatePost()
    ctx = Context({'app': appCtx})

    responseDict = reflect_web.preCalc(parms, ctx)
    logging.info(responseDict)

    raise SuccessResp(responseDict)


# Handle the retrieve reflect attribute route.
@app.route('/reflect/attrId/<string:attrId>', methods=['GET'])
def getRefAttr(attrId):
    """Returns reflection request JSON.
    define return schema
    """
    logging.info('Reflection get request, attrid: ' + attrId)
    responseDict = reflect_web.getReflectionAttr(attrId)
    raise SuccessResp(responseDict)


# Handle the route to test.
@app.route('/test', methods=['POST', 'GET'])
def testRoute():
    raise SuccessResp('just testing data server')


initialize()
