
# Retrieve view data for a map.

import os, csv
from util_web import ErrorResp, stringToFloatOrInt


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


'''future:
def highlightAttrNode(data, appCtx):

    # Highlight a list of nodes and attributes on an existing map.
    
    #


    state generated:
    {
        'project': mapId,
        'layoutIndex': layoutIndex,
        'dynamic_attrs': {
            'TCGA-01': {
            }
        }
    }
    data in:
    {
       "map": "CKCC/v1",
       "layout": "mRNA",
       "attributes": [
           "gender",
           "subType",
           ...
       ],
       "nodes": [
           "TCGA-01",
           "TCGA-02",
           ...
       ],
    }
'''


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
            #for j, row in f:
            for j, row in enumerate(f.__iter__()):
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
