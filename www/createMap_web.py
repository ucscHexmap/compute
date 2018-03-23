
# createMap_web.py
# For the createMap calculation this handles:
#   - validation of received input
#   - mapping between relative data IDs to absolute paths
#   - http response and code
#   - completion callback to check log for success

from os import path
from argparse import Namespace
import validate_web as validate
import layout
import job

def formatGeneratedUrls(result, msg):

    # Add any urls generated for uploaded layout input files.
    for url in result['layoutInputUrl']:
        msg += 'Your layout input data may be accessed in the future ' + \
            'with:\n\n' + url + '\n\n'

    # Add any urls generated for uploaded color attribute files.
    for url in result['colorAttributeUrl']:
        msg += 'Your color attributes data may be accessed in the future ' + \
            'with:\n\n' + url + '\n\n'


def formatEmailError(result, ctx):

    # Format the error for sending in an email.
    msg = 'There was an error while calculating results for createMap'
    msg += ' for map: ' + ctx.map
    if result != None:
        msg += '\n\nerror: ' + result['error'] + '\n\n'
    formatGeneratedUrls(result, msg)
    return msg


def formatEmailResult(result, ctx):

    # Format the results for sending in an email.
    msg = 'See your new map: ' + ctx.map + ' at:\n\n' + result['url'] + '\n\n'
    formatGeneratedUrls(result, msg)
    return msg


def checkLog(result, ctx):

    # Open the log file in the result returned.
    try:
        f = open(result['logFile'], 'r')
    except (e):
        raise Exception('Could not open log file')
    
    # Check for the success message in the log file.
    successMsg = 'Visualization generation complete!'
    success = False
    for line in f:
        if line.find(successMsg) > -1:
            success = True
            break
    if not success:
        raise Exception('Error when creating a map. Calc script had an ' + \
            'unknown error. ' + 'logfile: ' + logFile)


def generateDataUrls(result, parms, ctx):

    # Save any new data URLs in the results.
    if 'layoutInputDataId' in parms:
        result['layoutInputUrl'] = []
        for dataId in parms['layoutInputDataId']:
            result['layoutInputUrl'].append(
                ctx.app.dataServer + '/data/' + dataId)
    if 'colorAttributeDataId' in parms:
        result['colorAttributeUrl'] = []
        for dataId in parms['colorAttributeDataId']:
            result['colorAttributeUrl'].append(
                ctx.app.dataServer + '/data/' + dataId)


def calcMain(parms, ctx):

    # The main process in which the job executes.
    # Use standard exceptions here to report errors.
    # @param parms: the parameters for the operation
    # @param ctx: the job context
    # @returns: (status, result) where the status is 'Success' or 'Error'
    #           and the result depends on the status:
    #               Success: a dict like:
    #                   {
    #                       'status': 'Success',
    #                       'url': 'https://tumormap.ucsc.edu/?p=myMap',
    #                       'logFile': <logFileName>
    #                   }
    #               Error: a dict containing one of the below:
    #                   {'error': <message>}
    #                   {'error': <message>, 'stackTrace': <trace>}

    # Fix up relative paths and map any newer parm names to old parm names
    # that are expected by the calc function. If we want this to become a public
    # API, we need to accept the new names only.
    opts = Namespace()
    
    # layoutInput is required: accept either a file location relative to the
    # data root, or a URL.
    if 'layoutInputDataId' in parms:
        opts.layoutInputFile = \
            [path.join(ctx.app.dataRoot, parms['layoutInputDataId'])]
    elif 'layoutInputUrl' in parms:
        opts.layoutInputFile = [parms['layoutInputUrl']]

    # names and directory are required
    opts.names = [parms['layoutInputName']]
    opts.directory = path.join(ctx.app.dataRoot, parms['outputDirectory'])

    # colorAttribute is optional: accept either a file location relative to the
    # data root, or a URL.
    if 'colorAttributeDataId' in parms:
        opts.scores = \
            [path.join(ctx.app.dataRoot, parms['colorAttributeDataId'])]
    elif 'colorAttributeUrl' in parms:
        opts.scores = [parms['colorAttributeUrl']]

    # The rest of these are optional.
    if 'zeroReplace' in parms:
        opts.zeroReplace = parms['zeroReplace']
    if 'noLayoutIndependentStats' in parms:
        opts.associations = not parms['noLayoutIndependentStats']
    if 'noLayoutAwareStats' in parms:
        opts.mutualinfo = not parms['noLayoutAwareStats']

    # Call the calc function.
    result = {
        'logFile': layout.makeMapUIfiles(opts),
    }

    # Save any new data URLs in the results.
    generateDataUrls(result, parms, ctx)

    # Check the calc log for success.
    checkLog(result, ctx)

    # Save the url to access the new map.
    if 'viewServer' in parms:
        viewServer = parms['viewServer']
    else:
        viewServer = ctx.app.viewServer

    result['url'] = viewServer + '/?p=' + ctx.map

    return "Success", result


def _validateParms(data):

    # Validate the query.
    # @param data: data received in the http post request
    # @return: nothing

    # Checks on required parameters
    validate.map(data, True)
    validate.layoutInput(data, required=True)
    validate.layoutInputName(data, required=True)
    # TODO: validate.outputDirectory(data, required=True)

    # Checks on optional parameters
    #validate.authGroup(data)
    validate.email(data)
    validate.neighborCount(data)
    validate.colorAttribute(data)
    #validate.firstColorAttribute(data)
    #validate.colormapDataId(data)
    #validate.layoutAwareStats(data)
    #validate.layoutIndependentStats(data)
    #validate.viewServer(data)


def preCalc(data, ctx):

    # The entry point from the URL routing.
    # @param data: data from the HTTP post request
    # @param ctx: job context
    # @return: result of _calcComplete()
    
    _validateParms(data)
    
    # Execute the job immediately for debugging.
    #return calcMain(data, ctx)
    
    # Add this task to the job queue.
    return job.add(data['email'], 'createMap', data, ctx)
