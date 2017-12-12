
# www
#
import os, json, traceback, logging
from flask import Flask, request, jsonify, current_app, Response
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename

from util_web import SuccessResp, SuccessRespNoJson, ErrorResp, Context
import validate_web as validate
import placeNode_web

# Set up the flask application where app.config is only accessed in this file.
app = Flask(__name__)

# Other local vars.
allowableViewers = os.environ.get('ALLOWABLE_VIEWERS').split(',')

# Make cross-origin AJAX possible
CORS(app)

# Set up the application context used by all threads.
appCtxDict = {
    'adminEmail': os.environ.get('ADMIN_EMAIL'),
    'dataRoot': os.environ.get('DATA_ROOT', 'DATA_ROOT_ENV_VAR_MISSING'),
    'debug': os.environ.get('DEBUG', 0),
    'hubPath': os.environ.get('HUB_PATH'),
    'unitTest': int(os.environ.get('UNIT_TEST', 0)),
    'viewServer': os.environ.get('VIEWER_URL', 'http://hexdev.sdsc.edu'),
}
appCtxDict['jobQueuePath'] = os.path.join(appCtxDict['hubPath'], '../computeDb/jobQueue.db')
appCtxDict['viewDir'] = os.path.join(appCtxDict['dataRoot'], 'view')
appCtx = Context(appCtxDict)

# Set up logging
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
    response = jsonify(success.to_dict())
    response.status_code = 200
    #logging.info('success json response: ' + str(response))
    return response

# Register the success handler that doesn't convert to json
@app.errorhandler(SuccessRespNoJson)
def successResponseNoJson(success):
    response = success.to_dict()
    response.status_code = 200
    #logging.info('success no json response: ' + str(response))
    return response

# Register the error handler
@app.errorhandler(ErrorResp)
def errorResponse(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    logging.error('Request failed with: ' + str(response.status_code) + ': ' + \
        str(response) + " " + error.message)
    return response

@app.errorhandler(Exception)
def unhandledException(e):
    trace = traceback.format_exc()
    errorMessage = repr(e)
    # Build response.
    rdict = {
            "traceback" : trace,
            "error" : errorMessage,
            }
    response = jsonify(rdict)
    response.status_code = 500

    logging.error("Uncaught exception: \n" + trace)

    return response

# Handle route to upload files
@app.route('/upload/<path:dataId>', methods=['POST'])
def upload(dataId):
        
    # If the caller does not include a file property in the post
    # there is nothing to upload. So bail.
    if 'file' not in request.files:
        raise ErrorResp('No file property provided for upload', 400)
    
    file = request.files['file']

    # If a browser user does not include a file, the browser submits an
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
    except Exception as e:
        #traceback.print_exc()
        raise ErrorResp(repr(e), 500)

    raise SuccessRespNoJson(result)

# Handle data/<dataId> routes which are data requests by data ID.
@app.route('/data/<path:dataId>', methods=['GET'])
def dataRoute(dataId):
    logging.debug('Received data request for ' + dataId)
    dataRouteInner(dataId)

# Handle data404ok/<dataId> routes which are data requests by data ID.
# A 404 is ok to return here, so we do it as 'success' so that errors
# will not be thrown on the client console.
@app.route('/dataOk404/<path:dataId>', methods=['GET'])
def dataRouteOk404(dataId):
    logging.debug('Received data OK 404 request for ' + dataId)
    dataRouteInner(dataId, True)

# Handle query/<operation> routes
@app.route('/query/<string:operation>', methods=['POST'])
def queryRoute(operation):
    logging.info('Received query operation: ' + operation)
    dataIn = validatePost()
    try:
        if operation == 'overlayNodes':
            jobCtx = Context({'app': appCtx})
            result = placeNode_web.preCalc(dataIn, jobCtx)
        else:
            raise ErrorResp('URL not found', 404)
    except ErrorResp:
         # Re-raise this error to send the response.
        raise
    except Exception as e:
        traceback.print_exc()
        raise ErrorResp(repr(e), 500)

    logging.info('Success with query operation: ' + operation)
    raise SuccessResp(result)

# Handle the route to test
@app.route('/test', methods=['POST', 'GET'])
def testRoute():

    logging.debug('testRoute current_app: ' + str(current_app))

    raise SuccessResp('just testing')
