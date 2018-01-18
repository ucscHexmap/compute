
# Main module for the http server, including all routes.

import os, traceback, logging, json
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename

import createMap_web
import job
import jobTestHelper_web
import placeNode_web
import reflect_web
from util_web import SuccessResp, SuccessRespNoJson, ErrorResp, Context, \
    reportRouteError
import validate_web as validate

# Set up the flask application.
app = Flask(__name__)

# Set up the application context used by all threads.
def contextInit ():
    global appCtx
    appCtx = Context({})
    appCtx.adminEmail = os.environ.get('ADMIN_EMAIL')
    appCtx.dataRoot = os.environ.get('DATA_ROOT', 'DATA_ROOT_ENV_VAR_MISSING')
    appCtx.debug = os.environ.get('DEBUG', 0)
    appCtx.dev = int(os.environ.get('DEV', 0))
    appCtx.hubPath = os.environ.get('HUB_PATH')
    appCtx.unitTest = int(os.environ.get('UNIT_TEST', 0))
    appCtx.viewServer = os.environ.get('VIEWER_URL', 'http://hexdev.sdsc.edu')

    # Derived context.
    appCtx.databasePath = os.environ.get('DATABASE_PATH', appCtx.hubPath + '/../computeDb')
    appCtx.jobQueuePath = os.path.abspath(
        os.path.join(appCtx.databasePath, 'jobQueue.db'))
    appCtx.jobProcessPath = appCtx.hubPath + '/www/jobProcess.py'
    appCtx.viewDir = os.path.join(appCtx.dataRoot, 'view')
    jobStatusUrl = os.environ['WWW_SOCKET'] + '/jobStatus/jobId/'
    if os.environ['USE_HTTPS'] == '1':
        appCtx.jobStatusUrl = 'https://' + jobStatusUrl
    else:
        appCtx.jobStatusUrl = 'http://' + jobStatusUrl
    return appCtx

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
    logging.info('Allowable viewers: ' + str(allowableViewers))

# Initialize the app.
def initialize():

    # Other local vars.
    global allowableViewers
    allowableViewers = os.environ.get('ALLOWABLE_VIEWERS').split(',')

    # Make cross-origin AJAX possible
    CORS(app)

    contextInit()
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
    statusCode, responseStr = str(response.status_code), str(response)
    return response

# Register the unhandled Exception handler
@app.errorhandler(Exception)
def unhandledException(e):
    trace = traceback.format_exc()
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

# Handle route to upload files
@app.route('/upload/<path:dataId>', methods=['POST'])
def upload(dataId):
        
    # If the client does not include a file property in the post
    # there is nothing to upload. So bail.
    if 'file' not in request.files:
        raise ErrorResp('No file property provided for upload', 400)
    
    file = request.files['file']

    # If a browser user does not select a file, the browser submits an
    # empty file property. So bail.
    if file.filename == '':
        raise ErrorResp('No file provided for upload', 400)
        
    filename = secure_filename(file.filename)
    path = os.path.join(appCtx.dataRoot, dataId)
    
    # Make the directories if they are not there.
    try:
        os.makedirs(path[:path.rfind('/')], 0770)
    except Exception:
        pass
    
    # Save the file
    try:
        file.save(path)
    except Exception:
        raise ErrorResp('Unable to save file.', 500)
    
    raise SuccessResp('upload of ' + filename + ' complete')

def dataRouteInner(dataId, ok404=False):
    """
    # For now, let anyone read.
    # Only allow authorized view servers to pull data.
    try:
        origin = request.environ['HTTP_ORIGIN']
    except Exception:
        raise ErrorResp('http-origin not defined', 400)
    if not origin in app.config['ALLOWABLE_VIEWERS']:
        raise ErrorResp('Unauthorized http-origin: ' + origin, 400)
    """

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
@app.route('/dataOk404/<path:dataId>', methods=['GET'])
def dataRouteOk404(dataId):
    dataRouteInner(dataId, True)

# Handle get all jobs route
@app.route('/getAllJobs', methods=['GET'])
def getAllJobsRoute():
    result = job.getAll(appCtx.jobQueuePath)
    raise SuccessResp(result)

# Handle jobStatus route
@app.route('/jobStatus/jobId/<int:jobId>', methods=['GET'])
def jobStatusRoute(jobId):
    result = job.getStatus(jobId, appCtx.jobQueuePath)
    raise SuccessResp(result)

# Handle query/jobTestHelper routes
@app.route('/query/jobTestHelper', methods=['POST'])
def queryJobTestHelperRoute():
    result = jobTestHelper_web.preCalc(validatePost(), Context({'app': appCtx}))
    raise SuccessResp(result)

# Handle query/createMap route.
@app.route('/query/createMap', methods=['POST'])
def queryCreateMapRoute():
    result = createMap_web.preCalc(validatePost(), Context({'app': appCtx }))
    raise SuccessResp(result)

# Handle query/overlayNode route, older version of placeNode
@app.route('/query/overlayNodes', methods=['POST'])
def queryOverlayNodesRoute():
    result = placeNode_web.preCalc(validatePost(),
        Context({'app': appCtx, 'overlayNodes': True}))
    raise SuccessResp(result)

# Handle query/placeNode routes
@app.route('/query/placeNode', methods=['POST'])
def queryPlaceNodeRoute():
    result = placeNode_web.preCalc(validatePost(), Context({'app': appCtx}))
    raise SuccessResp(result)

# Handle reflect/metadata routes
@app.route(
'/reflect/metaData/majorId/<string:majorId>/minorId/<string:minorId>',
    methods=['GET']
)
def getReflectMetaData(majorId, minorId):
    responseDict = reflect_web.getReflectionMetaData(majorId, minorId)
    raise SuccessResp(responseDict)

# Handle reflect routes
@app.route('/reflect', methods=['POST'])
def reflectionRequest():
    """
    JSON post
        {
        dataType : "str"
        userId : "not Needed now"n
        mapId : "SuchandSuch/SampleMap"
        toMapId: ""
        featOrSamp: "feature" anything else assumes samples
        nodeIds: an array of nodeIds
        rankCategories : boolean, if true returns ranked categories.
        selectionName : used to create the new reflection Name.
        }
    JSON response:
       {
        url : /reflect/attrId/<string:fileId>,
        haveData : 123
        }
    """
    logging.info('Reflection requested')
    parms = validatePost()
    responseDict = reflect_web.calc(parms)

    raise SuccessResp(responseDict)

# Handle reflect/attrId routes
@app.route('/reflect/attrId/<string:attrId>', methods=['GET'])
def getRefAttr(attrId):
    """Returns reflection request JSON."""
    logging.info('Reflection get request, attrid: ' + attrId)
    responseDict = reflect_web.getReflectionAttr(attrId)
    raise SuccessResp(responseDict)

# Handle the route to test
@app.route('/test', methods=['POST', 'GET'])
def testRoute():
    raise SuccessResp('just testing data server')

initialize()
