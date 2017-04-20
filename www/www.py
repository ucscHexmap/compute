
# www
#
import os, json, traceback, logging
from flask import Flask, request, jsonify, current_app
from flask_cors import CORS, cross_origin

import webUtil
from webUtil import SuccessResp, ErrorResp
import placeNode_web

# Set up the flask application
app = Flask(__name__)
app.config['UNIT_TEST'] = int(os.environ.get('UNIT_TEST', 0))
app.config['DEBUG'] = int(os.environ.get('DEBUG'), 0)

# Make cross-origin AJAX possible
CORS(app)

# Set up the context, mostly from environment variables
ctx = {
    # default the view server URL to that of development
    'viewerUrl': os.environ.get('VIEWER_URL', 'http://hexdev.sdsc.edu'),
    'dataRoot': os.environ.get('DATA_ROOT', 'DATA_ROOT_ENV_VAR_MISSING'),
}

# Set up logging
logFormat = '%(asctime)s %(levelname)s: %(message)s'
if app.config['UNIT_TEST']:

    # Use critical level to disable all messages so unit tests only output
    # unit test errors.
    logging.basicConfig(level=logging.CRITICAL, format=logFormat)
elif app.config['DEBUG']:
    logging.basicConfig(level=logging.DEBUG, format=logFormat)
else:
    logging.basicConfig(level=logging.WARNING, format=logFormat)

# Validate a post
def validatePost():
    if request.headers['Content-Type'] != 'application/json':
        raise ErrorResp('Content-Type must be application/json')
    try:
        dataIn = request.get_json()
    except:
        raise ErrorResp('Post content is invalid JSON')
    return dataIn

# Register the success handler
@app.errorhandler(SuccessResp)
def successResponse(success):
    response = jsonify(success.to_dict())
    response.status_code = 200
    #logging.info('response: ' + str(response))
    return response

# Register the error handler
@app.errorhandler(ErrorResp)
def errorResponse(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    data = json.loads(response.data)
    if 'error' in data:
        msg = data['error']
    else:
        msg = 'unknown error'
    logging.error('Request failed with: ' + str(response.status_code) + ': ' + \
        str(response) + " " + msg)
    return response

"""
# Handle file request routes by view file name
@app.route('/file/<string:filename>/<path:map>', methods=['POST', 'GET'])
def queryFile(filename, map):
"""

# Handle query/<operation> routes
@app.route('/query/<string:operation>', methods=['POST'])
def queryRoute(operation):

    logging.info('Received query operation: ' + operation)
    dataIn = validatePost()

    if operation == 'overlayNodes':
        result = placeNode_web.calc(dataIn, ctx)
        
    else:
        raise ErrorResp('URL not found', 404)

    logging.info('Success with query operation: ' + operation)
    raise SuccessResp(result)

# Handle the route to test
@app.route('/test', methods=['POST', 'GET'])
def testRoute():

    app.logger.debug('testRoute current_app: ' + str(current_app))

    raise SuccessResp('just testing')
