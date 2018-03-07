
# placeNode_web.py
# For the placeNode calculation this handles:
#   - validation of received input
#   - mapping between mapID and layout to data file locations
#   - http response and code

import os
import validate_web as validate
import util_web
from util_web import ErrorResp, createBookmark
import placeNode
import compute_sparse_matrix
import utils
import pandas as pd
import numpy as np
import typeTransforms
import job

def formatEmailResult(result):

    # Format the results for sending in an email.
    
    # Find all of the urls.
    url = {}
    for node in result['nodes']:
        url[node] = result['nodes'][node]['url']
    uniqueUrls = set(url.values())
    msg = '\nFor placing the new nodes:'
    
    # Include each node.
    for nodeName in sorted(result['nodes'].keys()):
        msg += '\n' + nodeName
        if len(uniqueUrls) > 1:
            msg += ': ' + url[nodeName]

    # If there is only one url, include that one.
    if len(uniqueUrls) < 2:
        msg = '\n' + list(uniqueUrls)[0] + '\n' + msg

    return msg

def _checkDuplicateRowError(error):
    """
    Checks to see if there is a duplicate row error and sends a more meaningful
    error message.
    @param e_message: The message from the caught exception
    @return: None or Raises an ValueError with a pertinant message
    """
    e_message = error.message
    # These messages are created in comupte_sparse_matrix.common_rows function.
    if e_message == "Duplicate rows in first matrix.":
        raise ValueError("Duplicate rows in new nodes input causing failure.")
    if e_message == "Duplicate rows in second matrix.":
        raise ValueError("Duplicate rows in feature matrix causing failure,"
                         "this map will be unable to complete node placement."
                         "Build a new map without duplicate row names.")

    raise error

def _postCalc(result, ctx):
    '''
    Create bookmarks and send email from a calculation result.
    @param result: results from the calculation
    @param ctx: global context
    @return: ('success', result)
    '''
    if 'error' in result:
    
        # Notify user & save result.
        result['error'] = 'Error in placing nodes.\n\n' + result['error']
        #util_web.sendResultsEmail(dataIn, 'Error in placing nodes.\n\n' +
        #    result['error'], ctx.app)
        return 'Error', result

    dataIn = ctx.dataIn
    
    # Be sure we have a view server
    if not 'viewServer' in dataIn:
        dataIn['viewServer'] = ctx.app.viewServer

    # Format the result as client state in preparation to create a bookmark
    state = {
        'page': 'mapPage',
        'project': dataIn['map'] + '/',
        'layoutIndex': ctx.layoutIndex,
        'shortlist': [],
        'overlayNodes': {},
        'dynamic_attrs': {},
    }
    mailMsg = ''
    active_layer = None

    # Populate state for each node
    needFirstLayer = True
    for node in result['nodes']:
        nData = result['nodes'][node]
        state['overlayNodes'][node] = { 'x': nData['x'], 'y': nData['y'] }
        
        # Build the neighbor places layer
        attr = node + ': ' + dataIn['layout'] + ': neighbors'
        if needFirstLayer:
            needFirstLayer = False
            active_layer = attr
        state['shortlist'].append(attr)
        state['dynamic_attrs'][attr] = {
            'dynamic': True,
            'dataType': 'binary',
            'data': {},
        }
        
        # Build the neighbor values layer
        attrV = node + ': ' + dataIn['layout'] + ': neighbor values'
        state['shortlist'].append(attrV)
        state['dynamic_attrs'][attrV] = {
            'dynamic': True,
            'dataType': 'continuous',
            'data': {},
        }
        
        # Add the values to the new layers
        for neighbor in nData['neighbors']:
            state['dynamic_attrs'][attr]['data'][neighbor] = 1
            state['dynamic_attrs'][attrV]['data'][neighbor] = \
                nData['neighbors'][neighbor]

        # Set the number of values in the state for each attribute
        state['dynamic_attrs'][attr]['n'] = \
            len(state['dynamic_attrs'][attr]['data'])
        state['dynamic_attrs'][attrV]['n'] = \
            len(state['dynamic_attrs'][attrV]['data'])

        # If individual Urls were requested, create a bookmark for this node
        if 'individualUrls' in dataIn and dataIn['individualUrls']:
        
            # Set the active_layer to color the map.
            state['active_layers'] = [attr]
            
            # Create the bookmark.
            bData = createBookmark(state, dataIn['viewServer'], ctx)
            result['nodes'][node]['url'] = bData['bookmark']
            mailMsg += ' \n' + node + ': ' + bData['bookmark']

            # Clear the node data to get ready for the next node
            state['overlayNodes'] = {}
            state['dynamic_attrs'] = {}
            state['shortlist'] = [];
        
    # If individual urls were not requested, create one bookmark containing all
    # nodes and return that url for each node
    if not 'individualUrls' in dataIn or not dataIn['individualUrls']:
        
        # Set the active layer to color the map.
        state['active_layers'] = [active_layer]

        # Create the bookmark.
        bData = createBookmark(state, dataIn['viewServer'], ctx)
        for node in result['nodes']:
            result['nodes'][node]['url'] = bData['bookmark']
            mailMsg += ', ' + node
        
        mailMsg = mailMsg[2:] + '\n' + bData['bookmark']

    return 'Success', result

def _outputToDict(neighboorhood, xys, urls):
    '''
    This function takes the output from the newplacement call
      into the expected format
    @param neighboorhood: pandas df
    @param xys: pandas df
    @param urls: an array of URLs
    @return: dictionary to be turned into a JSON str
    '''
    #return dictionary to populate with results
    retDict = {"nodes":{}}

    #seperating the columns of the neighborhood df
    # for processing
    newNodes  = neighboorhood[neighboorhood.columns[0]]
    neighbors = neighboorhood[neighboorhood.columns[1]]
    scores    = neighboorhood[neighboorhood.columns[2]]
    #grab column names for indexing
    xcol = xys.columns[0]
    ycol = xys.columns[1]

    for i,node in enumerate(set(newNodes)):
        maskArr = np.array(newNodes == node)
        retDict['nodes'][node] = {}
        retDict['nodes'][node]['neighbors'] = dict(zip(neighbors.iloc[maskArr],
                                                       scores.iloc[maskArr]))
        #add urls to the return struct
        #retDict['nodes'][node]['url'] = urls[i]
        retDict['nodes'][node]['x'] = xys.loc[node,xcol]
        retDict['nodes'][node]['y'] = xys.loc[node,ycol]

    return retDict

def _putDataIntoPythonStructs(featurePath, xyPath, nodesDict):
    '''
    takes in the filenames and nodes dictionary needed for placement calc
    @param featurePath:
    @param xyPath:
    @param tabSepArray:
    @return:
    '''
    return (
        typeTransforms.numpyToPandas(
            *compute_sparse_matrix.read_tabular(featurePath)
        ),
        utils.readXYs(xyPath),
        _nodesToPandas(nodesDict)
    )

def _nodesToPandas(pydict):
    '''
    Input the json['nodes'] structure and outputs pandas df.
    Uses same processing pipeline as compute sparse matrix for input.
    @param pydict: the dataIn['nodes'] structure,
                   currently a dict of dicts {columns -> {rows -> values}}
    @return: a pandas dataframe
    '''
    df = pd.DataFrame(pydict, dtype=float)
    utils.duplicate_columns_check(df)
    df = compute_sparse_matrix.processInputData(df,
                                                numeric_flag=True,
                                                replaceNA=False
                                                )

    return df

def _getBackgroundData(data, ctx):
    '''
    Find the clustering data file for this map and layout.
    @param data: background data of the existing map
    @param ctx: global context
    @return: cluster data file path and the pre-bin xy coordinates
    '''
    try:
        layouts = ctx.getMapMetaData(data['map'])['layouts']
        clusterData = layouts[data['layout']]['clusterData']
        clusterDataFile = os.path.join(ctx.app.dataRoot, clusterData)
    except Exception as e:
        raise Exception('Clustering data not found for layout: ' + \
            data['layout'])

    # Find the index of the layout
    ctx.layoutIndex = \
        ctx.app.getLayoutIndex(data['layout'], data['map'])

    # Find the xyPosition file
    xyPositionFile = os.path.join(
        ctx.mapDir, 'assignments' + str(ctx.layoutIndex) + '.tab')

    return clusterDataFile, xyPositionFile

def calcMain(dataIn, ctx):
    ctx.mapDir = ctx.app.pathToMap(dataIn['map'])

    # Find the helper data needed to place nodes
    clusterDataFile, xyPositionFile = _getBackgroundData(dataIn, ctx)

    # Set any optional parms, letting the calc script set defaults.
    if 'neighborCount' in dataIn:
        top = dataIn['neighborCount']
    else:
        top = 6 # TODO: this default should be set in the calc module.

    # Make expected python data structs
    referenceDF, xyDF, newNodesDF = _putDataIntoPythonStructs(
        clusterDataFile,
        xyPositionFile,
        dataIn['nodes']
     )

    # Call the calc script.
    try:
        neighboorhood, xys, urls = placeNode.placeNew(
            newNodesDF,
            referenceDF,
            xyDF,
            top,
            dataIn['map'],
            num_jobs=1
        )

    except ValueError as error:
        # Make useful error message if we recognize the error.
        _checkDuplicateRowError(error)

    #format into python struct
    result = _outputToDict(neighboorhood, xys, urls)

    ctx.dataIn = dataIn
    
    if hasattr(ctx, "callingOldApi"):
        # Respond to request here when using the older API.
        status, result = _postCalc(result, ctx)
        return result
    
    # Save the result in the job queue.
    return _postCalc(result, ctx)

def _validateParms(data):
    '''
    Validate the query.
    @param data: data received in the http post request
    @return: nothing
    '''
    # Basic checks on required parameters
    validate.map(data, True)
    validate.layout(data, True)
    if 'nodes' not in data:
        raise ErrorResp('nodes parameter missing or malformed')
    if not isinstance(data['nodes'], dict):
        raise ErrorResp('nodes parameter should be a dictionary')
    if len(data['nodes'].keys()) < 1:
        raise ErrorResp('there are no nodes in the nodes dictionary')
    
    # Basic checks on optional parameters
    validate.email(data)
    validate.viewServer(data)
    if 'neighborCount' in data and \
        (not isinstance(data['neighborCount'], int) or \
        data['neighborCount'] < 1):
        raise ErrorResp('neighborCount parameter should be a positive integer')

def preCalc(dataIn, ctx):
    '''
    The entry point from the www URL routing.
    @param dataIn: data from the HTTP post request
    @param ctx: global context
    @return: result of calcComplete()
    '''
    _validateParms(dataIn)

    if hasattr(ctx, "callingOldApi"):
        # Execute the job immediately when using the older API.
        return calcMain(dataIn, ctx)

    # Add the job to the job queue.
    email = None
    if 'email' in dataIn:
        email = dataIn['email']
    return job.add(email, 'placeNode', dataIn, ctx)

