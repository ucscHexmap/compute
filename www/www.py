
# www
#
import os, json, traceback, logging
from flask import Flask, request, jsonify, current_app, Response
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename

import util_web
from util_web import SuccessResp, SuccessRespNoJson, ErrorResp
import placeNode_web

# Set up the flask application where app.config is only accessed in this file.
app = Flask(__name__)
app.config['UNIT_TEST'] = int(os.environ.get('UNIT_TEST', 0))
app.config['DEBUG'] = int(os.environ.get('DEBUG'), 0)
# The origin is checked for some functions that we only want the viewer to do.
app.config['ALLOWABLE_VIEWERS'] = os.environ.get('ALLOWABLE_VIEWERS').split(',')

# Make cross-origin AJAX possible
CORS(app)

# Set up the context that will be passed to down-stream calls.
ctx = {
    # default the view server URL to that of development
    'viewerUrl': os.environ.get('VIEWER_URL', 'http://hexdev.sdsc.edu'),
    'dataRoot': os.environ.get('DATA_ROOT', 'DATA_ROOT_ENV_VAR_MISSING'),
    'adminEmail': os.environ.get('ADMIN_EMAIL'),
}

# Set up logging
logFormat = '%(asctime)s %(levelname)s: %(message)s'
logLevel = None
if app.config['UNIT_TEST']:

    # Use critical level to disable all messages so unit tests only output
    # unit test errors.
    logging.basicConfig(level=logging.CRITICAL, format=logFormat)
    logLevel = 'CRITICAL'
elif app.config['DEBUG']:
    logging.basicConfig(level=logging.DEBUG, format=logFormat)
    logLevel = 'DEBUG'
else:
    logging.basicConfig(level=logging.INFO, format=logFormat)
    logLevel = 'INFO'

logging.info('WWW server started with log level: ' + logLevel)

# Validate a post
def validatePost():
    if request.headers['Content-Type'] != 'application/json':
        raise ErrorResp('Content-Type must be application/json')
    try:
        dataIn = request.get_json()
    except:
        raise ErrorResp('Post content is invalid JSON')
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
    path = os.path.join(ctx['dataRoot'], dataId)
    
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

# Handle data/<dataId> routes which are data requests by data ID.
@app.route('/data/<path:dataId>', methods=['GET'])
def dataRoute(dataId):
    logging.debug('Received data request for ' + dataId)
    
    # Only allow authorized view servers to pull data for now.
    if request.environ['HTTP_ORIGIN'] is None or \
        request.environ['HTTP_ORIGIN'] not in app.config['ALLOWABLE_VIEWERS']:
        raise ErrorResp('File not found', 404)
        
    # Not using flask's send_file() as it mangles files larger than 32k.
    try:
        with open(os.path.join(ctx['dataRoot'], dataId)) as f:
            data = f.read()
            result = Response(
                data,
                mimetype='text/csv',
                headers={'Content-disposition': 'attachment'})
    except IOError:
        raise ErrorResp('File not found', 404)
    except Exception as e:
        #traceback.print_exc()
        raise ErrorResp(repr(e), 500)

    raise SuccessRespNoJson(result)

# Handle query/<operation> routes
@app.route('/query/<string:operation>', methods=['POST'])
def queryRoute(operation):

    logging.info('Received query operation: ' + operation)
    dataIn = validatePost()
    try:
        if operation == 'overlayNodes':
            result = placeNode_web.calc(dataIn, ctx)
        else:
            raise ErrorResp('URL not found', 404)
    except ErrorResp:
         # Re-raise this error to send the response.
        raise
    except Exception as e:
        #traceback.print_exc()
        raise ErrorResp(repr(e), 500)

    logging.info('Success with query operation: ' + operation)
    raise SuccessResp(result)

# Handle the route to test
@app.route('/test', methods=['POST', 'GET'])
def testRoute():

    logging.debug('testRoute current_app: ' + str(current_app))

    raise SuccessResp('just testing')
