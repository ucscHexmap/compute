
# Retrieve view data for a map.

import os, csv
from util_web import ErrorResp, stringToFloatOrInt
import util_web
import validate_web as validate

def _highlightAttrNodeInner(data, appCtx):
    
    # Validate data
    validate.map(data, required=True)
    validate.layout(data)
    validate.attributes(data)
    validate.nodes(data)
    if not 'attributes' in data and not 'nodes' in data:
        raise ErrorResp('One or both of the parameters, ' + \
            '"attributes" and "nodes" must be provided.', 400)
    
    # Fill the required state for the bookmark.
    state = { 'project': data['map'] }
    
    if 'layout' in data:
        state['layoutName'] = data['layout']

    if 'nodes' in data:
    
        # Create a dynamic attribute of the node list for the state.
        attrData = {}
        for node in data['nodes']:
            attrData[node] = 1
        state['dynamicAttrs'] = {
            'yourNodes': {
                'data': attrData,
                'dataType': 'binary',
            }
        }
        state['shortlist'] = ['yourNodes']
        
    if 'attributes' in data:
    
        # Add the provided attributes in the shortlist state.
        if 'nodes' in data:
            state['shortlist'] += data['attributes']
        else:
            state['shortlist'] = data['attributes']
            
    return state


def highlightAttrNode(data, appCtx):

    # Highlight a list of nodes and attributes on an existing map.
    state = _highlightAttrNodeInner(data, appCtx)
    
    bookmark = util_web.createBookmark(state, appCtx.viewServer)
    return bookmark


def getAttrFilename(attrId, mapId, appCtx):

    # Read the layer summary file to find the attr file name.
    mapPath = os.path.join(appCtx.dataRoot, 'view', mapId)
    attrIndex = None
    try:
        with open(os.path.join(mapPath, 'layers.tab'), 'r') as f:
            f = csv.reader(f, delimiter='\t')
            for row in f:
                if row[0] == attrId:
                    attrIndex = row[1]
                    break
    except Exception as e:
        raise ErrorResp('With the attribute summary: ' + str(e), 500)

    return attrIndex


def getAttrList(mapId, appCtx):

    # Read the layer summary file to find the attr IDs.
    mapPath = os.path.join(appCtx.dataRoot, 'view', mapId)
    attrList = []
    try:
        with open(os.path.join(mapPath, 'layers.tab'), 'r') as f:
            f = csv.reader(f, delimiter='\t')
            for row in f:
                attrList.append(row[0])
    except Exception as e:
        raise ErrorResp('Retrieving attribute list: ' + str(e), 500)

    return attrList


def getLayoutList(mapId, appCtx):

    # Get the layout IDs of a map.

    # Read the layouts file to get the layouts.
    mapPath = os.path.join(appCtx.dataRoot, 'view', mapId)
    layoutList = []
    try:
        with open(os.path.join(mapPath, 'layouts.tab'), 'r') as f:
            f = csv.reader(f, delimiter='\t')
            for row in f:
                layoutList.append(row[0])
    except Exception as e:
        print 'exception: ', str(e)
    
        # There may be a file under the older name of "matrixnames.tab".
        try:
            with open(os.path.join(mapPath, 'matrixnames.tab'), 'r') as f:
                f = csv.reader(f, delimiter='\t')
                for row in f:
                    layoutList.append(row[0])
        except Exception as e:
            raise ErrorResp('With the layout list: ' + str(e), 500)

    # No layouts means we're done.
    if len(layoutList) < 1:
        raise ErrorResp('Layouts for map not found.', 404)

    return layoutList


def getFirstAttr(mapId, appCtx):

    # Get the dataType file which also contains the first attribute.
    try:
        mapPath = os.path.join(appCtx.dataRoot, 'view', mapId)
        path = os.path.join(mapPath, 'Layer_Data_Types.tab')
        first = None
        with open(path, 'r') as f:
            f = csv.reader(f, delimiter='\t')
            for row in f:
                type = row[0]
                for attr in row:
                    if type == 'FirstAttribute':
                        first = row[1]
                        break
    except Exception as e:
        raise ErrorResp('With finding default first attribute: ' + str(e), 404)

    return first


def getAttrById(attrId, mapId, appCtx):

    # Get an attribute's values by ID.
    attrIndex = getAttrFilename(attrId, mapId, appCtx)

    # No attr means we're done.
    if attrIndex == None:
        raise ErrorResp('Attribute not found.', 404)

    mapPath = os.path.join(appCtx.dataRoot, 'view', mapId)

    # Get the dataType.
    try:
        path = os.path.join(mapPath, 'Layer_Data_Types.tab')
        dataType = None
        with open(path, 'r') as f:
            f = csv.reader(f, delimiter='\t')
            
            # Convert the tsv to a dictionary arrays.
            types = {
            }
            for row in f:
                type = row[0]
                for attr in row:
                    if attr == attrId and type != 'FirstAttribute':
                        dataType = type
                        break
    except Exception as e:
        raise ErrorResp('With finding data type for attribute: ' + str(e), 404)

    # Get the values for this attr.
    try:
        path = os.path.join(mapPath, attrIndex)
        with open(path, 'r') as f:
            f = csv.reader(f, delimiter='\t')
            
            # Convert the tsv to a dictionary of two arrays.
            nodes = []
            values = []
            for j, row in enumerate(f.__iter__()):
                nodes.append(row[0])
                values.append(stringToFloatOrInt(row[1], dataType))
    except Exception as e:
        raise ErrorResp('With retrieving the attribute data: ' + str(e), 404)
    return { 'dataType': dataType, 'nodes': nodes, 'values': values }
