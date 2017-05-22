
# placeNode_web.py
# For the placeNode calculation this handles:
#   - validation of received input
#   - mapping between mapID and layout to data file locations
#   - http response and code

import os, json, types, requests, traceback, csv, logging
from argparse import Namespace
from flask import Response
import webUtil
from webUtil import SuccessResp, ErrorResp, getMapMetaData, \
    validateMap, validateLayout, validateEmail, validateViewServer
import placeNode
import compute_sparse_matrix
import utils
import pandas as pd
import StringIO
import numpy as np

def validateParameters(data):

    # Validate an overlayNodes query

    # Basic checks on required parameters
    validateMap(data, True)
    validateLayout(data, True)
    if 'nodes' not in data:
        raise ErrorResp('nodes parameter missing or malformed')
    if not isinstance(data['nodes'], dict):
        raise ErrorResp('nodes parameter should be a dictionary')
    if len(data['nodes'].keys()) < 1:
        raise ErrorResp('there are no nodes in the nodes dictionary')
    
    # Check for non-printable chars in names
    # TODO
    
    # Basic checks on optional parameters
    validateEmail(data)
    validateViewServer(data)
    if 'neighborCount' in data and \
        (not isinstance(data['neighborCount'], int) or \
        data['neighborCount'] < 1):
        raise ErrorResp('neighborCount parameter should be a positive integer')

def createBookmark(state, viewServer, ctx):

    # Create a bookmark

    # Ask the view server to create a bookmark of this client state
    # TODO fix the request to the view server to include cert
    try:
        bResult = requests.post(
            viewServer + '/query/createBookmark',
            #cert=(ctx['sslCert'], ctx['sslKey']),
            verify=False,
            headers = { 'Content-type': 'application/json' },
            data = json.dumps(state)
        )
    except:
        raise ErrorResp('Unknown error connecting to view server: ' +
            viewServer)

    bData = json.loads(bResult.text)
    if bResult.status_code == 200:
        return bData
    else:
        raise ErrorResp(bData)

def calcComplete(result, ctx):

    # The calculation has completed, so create bookmarks and send email
    
    dataIn = ctx['dataIn']

    #logging.debug('calcComplete: result: ' + str(result))
    
    if 'error' in result:
        raise ErrorResp(result['error'])

    # Be sure we have a view server
    if not 'viewServer' in dataIn:
        dataIn['viewServer'] = ctx['viewerUrl']

    # Find the first attribute if any
    firstAttribute = webUtil.getFirstAttribute(dataIn['map'], ctx)
    logging.error('### firstAttribute ' + str(firstAttribute))

    # Format the result as client state in preparation to create a bookmark
    state = {
        'page': 'mapPage',
        'project': dataIn['map'] + '/',
        'layoutIndex': ctx['layoutIndex'],
        'shortlist': [],
        'overlayNodes': {},
        'dynamic_attrs': {},
    }
    if firstAttribute:
        state['shortlist'].append(firstAttribute)
        state['first_layer'] = firstAttribute

    # Populate state for each node
    for node in result['nodes']:
        nData = result['nodes'][node]
        state['overlayNodes'][node] = { 'x': nData['x'], 'y': nData['y'] }
        
        # Build the neighbor places layer
        attr = node + ': ' + dataIn['layout'] + ': neighbors'
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
            state['dynamic_attrs'][attr]['data'][neighbor] = 1;
            state['dynamic_attrs'][attrV]['data'][neighbor] = \
                nData['neighbors'][neighbor];

        # Set the number of values in the state for each attribute
        state['dynamic_attrs'][attr]['n'] = \
            len(state['dynamic_attrs'][attr]['data']);
        state['dynamic_attrs'][attrV]['n'] = \
            len(state['dynamic_attrs'][attrV]['data']);

        # If individual Urls were requested, create a bookmark for this node
        if 'individualUrls' in dataIn and dataIn['individualUrls']:
            bData = createBookmark(state, dataIn['viewServer'], ctx)
            result['nodes'][node]['url'] = bData['bookmark']

            # Clear the node data to get ready for the next node
            state['overlayNodes'] = {}
            state['dynamic_attrs'] = {}
            state['shortlist'] = [];
        
    # If individual urls were not requested, create one bookmark containing all
    # nodes and return that url for each node
    if not 'individualUrls' in dataIn or not dataIn['individualUrls']:
        bData = createBookmark(state, dataIn['viewServer'], ctx)
        for node in result['nodes']:
            result['nodes'][node]['url'] = bData['bookmark']

    # TODO: Send completion Email
    """
    # a javascript routine:
    // Send email to interested parties
    var subject = 'tumor map results: ',
        msg = 'Tumor Map results are ready to view at:\n\n';
    
    _.each(emailUrls, function (node, nodeName) {
        msg += nodeName + ' : ' + node + '\n';
        subject += node + '  ';
    });
        
    if ('email' in dataIn) {
        sendMail(dataIn.email, subject, msg);
        msg += '\nAlso sent to: ' + dataIn.email;
    } else {
        msg += '\nNo emails included in request';
    }
    sendMail(ADMIN_EMAIL, subject, msg);
    """

    return result

def outputToDict(neighboorhood, xys, urls):
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

def putDataIntoPythonStructs(featurePath,xyPath,nodesDict):
    '''
    takes in the filenames and nodes dictionary needed for placement calc
    @param featurePath:
    @param xyPath:
    @param tabSepArray:
    @return:
    '''
    return (compute_sparse_matrix.numpyToPandas(
            *compute_sparse_matrix.read_tabular(featurePath)
                                                ),
            utils.readXYs(xyPath),
            nodesToPandas(nodesDict)
          )

def nodesToPandas(pydict):
    '''
    input the json['nodes'] structure and outputs pandas df
    This looks crazy because we needed to read in the new node data
    in the same way as the original feature matrix.
    @param pydict: the dataIn['nodes'] structure,
                   currently a dict of dicts {columns -> {rows -> values}}
    @return: a pandas dataframe
    '''
    df = pd.DataFrame(pydict)
    s_buf = StringIO.StringIO()
    #dump pandas data frame into buffer
    df.to_csv(s_buf,sep='\t')
    s_buf.seek(0)
    return compute_sparse_matrix.numpyToPandas(
            *compute_sparse_matrix.read_tabular(s_buf)
                                                )
def calcTestStub(newNodes, ctx):
    #print 'opts.newNodes', opts.newNodes
    
    ctx['layoutIndex'] = 0
    
    if 'testError' in newNodes:
        raise ErrorResp('Some error message or stack trace')
    elif len(newNodes) == 1:
        return {'nodes': {
            'newNode1': {
                'x': 73,
                'y': 91,
                'neighbors': {
                    'TCGA-BP-4790': 0.352,
                    'TCGA-AK-3458': 0.742,
                }
            },
        }}
    elif len(newNodes) > 1:
        return {'nodes': {
            'newNode1': {
                'x': 73,
                'y': 91,
                'neighbors': {
                    'TCGA-BP-4790': 0.352,
                    'TCGA-AK-3458': 0.742,
                }
            },
            'newNode2': {
                'x': 53,
                'y': 47,
                'neighbors': {
                    'neighbor1': 0.567,
                    'neighbor2': 0.853,
                }
            },
        }}
    else:
        raise ErrorResp('unknown test')

def getBackgroundData(data, ctx):

    # Find the clustering data file for this map and layout
    try:
        layouts = getMapMetaData(data['map'], ctx)['layouts']
        clusterData = layouts[data['layout']]['clusterData']
        clusterDataFile = os.path.join(ctx['dataRoot'], clusterData)
    except:
        raise ErrorResp(
            'Clustering data not found for layout: ' + data['layout'], 500)

    # Find the index of the layout
    ctx['layoutIndex'] = \
        webUtil.getLayoutIndex(data['layout'], data['map'], ctx)

    # Find the xyPosition file
    xyPositionFile = os.path.join(
        ctx['viewDir'], 'assignments' + str(ctx['layoutIndex']) + '.tab')
    
    return clusterDataFile, xyPositionFile

def calc(dataIn, ctx):

    # The entry point from the www URL routing
    validateParameters(dataIn)
    ctx['viewDir'] = os.path.join(ctx['dataRoot'], 'view', dataIn['map'])

    if 'testStub' in dataIn:
        result = calcTestStub(dataIn['nodes'], ctx)

        #print "### ctx['layoutIndex'] 2", ctx['layoutIndex']

    else:

        # Find the helper data needed to place nodes
        clusterDataFile, xyPositionFile = getBackgroundData(dataIn, ctx)

        # Set any optional parms, letting the calc script set defaults.
        if 'neighborCount' in dataIn:
            top = dataIn['neighborCount']
        else:
            top = 6

        #make expected python data structs
        try:
            referenceDF, xyDF, newNodesDF = \
             putDataIntoPythonStructs(clusterDataFile,
                                      xyPositionFile,
                                      dataIn['nodes'])
        except:
            raise ErrorResp('error on loading data', 500)

        # Call the calc script.
        neighboorhood, xys, urls = placeNode.placeNew(newNodesDF,referenceDF,
                                                      xyDF,top,dataIn['map'],
                                                      num_jobs=1)
        #format into JSON-like struct
        result = outputToDict(neighboorhood,xys,urls)


    ctx['dataIn'] = dataIn
    return calcComplete(result, ctx)
