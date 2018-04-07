
# Retrieve view data for a map.

import os, csv

def getAttrById(attrId, mapId, appCtx):

    # Get an attr's values given an attr name and map ID.

    # Read the layer summary file to find the attr file name.
    mapPath = os.path.join(appCtx.dataRoot, 'view', mapId)
    try:
        with open(os.path.join(mapPath, 'layers.tab'), 'r') as layers:
            layers = csv.reader(layers, delimiter='\t')
            attrIndex = None
            for row in layers:
                if row[0] == attrId:
                    attrIndex = row[1]
                    break
    except Exception (e):
        raise ErrorResp('With the attribute summary: ' + str(e), 500)

    # No attr means we're done.
    if attrIndex == None:
        raise ErrorResp('Attribute not found.', 404)

    # Get the values for this attr.
    try:
        path = os.path.join(mapPath, attrIndex)
        with open(path, 'r') as f:
            data = f.read()
    except:
        raise ErrorResp('With retrieving the attribute data: ' + str(e), 404)

    return data
