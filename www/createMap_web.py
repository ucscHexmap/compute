
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

def _postCalc(result, ctx):

    # Open the log file which is the result returned.
    logFile = result
    try:
        f = open(logFile,'r')
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

    result = {
        'url': ctx.viewServer + '/?p=' + ctx.map,
        'logFile': logFile
    }
    return "Success", result

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
    opts.layoutInputFile = \
        [path.join(ctx.app.dataRoot, parms['layoutInputDataId'])]
    opts.names = [parms['layoutInputName']]
    opts.directory = path.join(ctx.app.dataRoot, parms['outputDirectory'])
    if 'zeroReplace' in parms:
        opts.zeroReplace = parms['zeroReplace']
    if 'colorAttributeDataId' in parms:
        opts.scores = \
            [path.join(ctx.app.dataRoot, parms['colorAttributeDataId'])]
    if 'noLayoutIndependentStats' in parms:
        opts.associations = not parms['noLayoutIndependentStats']
    if 'noLayoutAwareStats' in parms:
        opts.mutualinfo = not parms['noLayoutAwareStats']

    # Call the calc function.
    result = layout.makeMapUIfiles(opts)
    
    # Save some parms we need for post-processing.
    if 'viewServer' in parms:
        ctx.viewServer = parms['viewServer']
    else:
        ctx.viewServer = ctx.app.viewServer

    return _postCalc(result, ctx)

def _validateParms(data):

    # Validate the query.
    # @param data: data received in the http post request
    # @return: nothing

    # Checks on required parameters
    validate.map(data, True)
    validate.layoutInputDataId(data, required=True)
    validate.layoutInputName(data, required=True)
    # TODO: validate.outputDirectory(data, required=True)

    # Checks on optional parameters
    #validate.authGroup(data)
    validate.email(data)
    validate.neighborCount(data)
    validate.colorAttributeDataId(data)
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
