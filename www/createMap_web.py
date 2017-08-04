
# createMap_web.py
# For the createMap calculation this handles:
#   - validation of received input
#   - mapping between relative data IDs to absolute paths
#   - http response and code
#   - completion callback to check log for success

import os, json, types, requests, traceback, csv, logging, datetime
from os import path
from subprocess import Popen
import validate_web as validate
from util_web import SuccessResp, ErrorResp, getMapMetaData
import layout

def _validateParameters(data):
    '''
    Validate the query.
    @param data: data received in the http post request
    @return: nothing
    '''
    #print 'validateParameters():data:', data
    # Checks on required parameters
    validate.map(data, True)
    validate.layoutInputDataId(data, True)
    validate.layoutInputName(data, True)

    # Checks on optional parameters
    validate.authGroup(data)
    validate.email(data)
    validate.neighborCount(data)
    validate.colorAttributeDataId(data)
    validate.firstColorAttribute(data)
    validate.colormapDataId(data)
    validate.layoutAwareStats(data)
    validate.layoutIndependentStats(data)
    validate.viewServer(data)

'''
def _calcComplete(result, ctx):

    # Check job status for createMap

    # Check for success in the log file which is the result returned.
    try:
        f = open(result,'r')
    catch:
        raise ErrorResp('Could not open log file')
    
    successMsg = 'Visualization generation complete!'
    for line in f:
        if line.find(successMsg) > -1:
            return result
    
    logging.error('Calc script had an unknown error; log file: ' + result)
    raise ErrorResp('Calc script had an unknown error', 500)

    # javascript:
    // Check the python layout log for success
    var log = fs.readFileSync(context.js_result, 'utf8');
    var log_array = log.split('\n');
    var success_msg = 'Visualization generation complete!';
    var success = _.find(log_array, function(line) {
        return line.indexOf(success_msg) > -1;
    });
    if (_.isUndefined(success)) {
    
        // Send the log to the admin & throw an error.
        var subject = 'Error when creating a map';
        var msg = 'log file: ' + result.data;
        sendMail(ADMIN_EMAIL, subject, msg);
        
        PythonCall.report_calc_result ({
            statusCode: 500,
            data: 'Calc script had an unknown error',
            }, context);
    } else {

        // Return the layout log file name
        PythonCall.report_calc_result(result, context);
    }
'''

argKeys = ['layoutInputFile', 'layoutName', 'colorAttributeFile', 'colormaps',
        'firstAttribute', 'outputDirectory', 'authGroup', 'zeroReplace',
        'attributeTags', 'noLayoutIndependentStats', 'noLayoutAwareStats']

def _apiToArgsList(dataIn, ctx):
    aList = []
    aList.append('--layoutInputFile')
    aList.append(path.join(ctx['dataRoot'], dataIn['layoutInputDataId']))
    aList.append('--layoutName')
    aList.append(dataIn['layoutInputName'])
    aList.append('--outputDirectory')
    aList.append(path.join(ctx['dataRoot'], 'view', dataIn['map']))
    return aList

def calc(dataIn, ctx):
    '''
    The entry point from the www URL routing.
    @param dataIn: data from the HTTP post request
    @param ctx: global context
    @return: result of _calcComplete()
    '''
    print 'calc()'
    _validateParameters(dataIn)
    
    # Prepend the data root to the data IDs,
    dataIn['layoutInputFile'] = path.join(ctx['dataRoot'],
        dataIn['layoutInputDataId'])
    if 'colorAttributeDataId' in dataIn:
        dataIn['colorAttributeFile'] = path.join(ctx['dataRoot'],
        dataIn['colorAttributeDataId'])
    if 'colormapDataId' in dataIn:
        dataIn['colormaps'] = path.join(ctx['dataRoot'],
        dataIn['colormapDataId'])

    argsList = _apiToArgsList(dataIn, ctx);

    print 'argsList', argsList

    print 'making job'
    
    #jobId = job.new(_calcComplete, ctx)
    jobId = '1111'

    print 'jobId:', jobId

    #raise SuccessResp({ 'status': 'Request received', 'jobId': jobId })

    #print 'made it past the SuccessResp'

    #return
    


    print 'before', str(datetime.datetime.now())
    returned = 'rats'
    
    try:
       returned = layout.withArgsAsList(argsList)
       #returned = subprocess.check_call(
       #     ["layout.withArgsAsList", '"' + dataIn + '"'])
    except:
        ErrorResp('Unknown error starting compute process', 500);

    print 'after', str(datetime.datetime.now())
    print 'returned', str(returned)

    '''
    # Be sure we have a view server
    if not 'viewServer' in dataIn:
        dataIn['viewServer'] = ctx['viewerUrl']

    jobId = job.new(newProcess, _calcComplete, ctx);
    '''
    
    return {
        'status': 'Request received',
        'jobId': jobId,
    }
