
import os, json, types, csv
from argparse import Namespace

class SuccessResp(Exception):

    # Define a success response class which converts to json.

    def __init__(self, data):
        Exception.__init__(self)
        self.data = data

    def to_dict(self):
        return self.data

class SuccessRespNoJson(Exception):

    # Define a success response class which does not convert to json.

    def __init__(self, data):
        Exception.__init__(self)
        self.data = data

    def to_dict(self):
        return self.data

class ErrorResp(Exception):

    # Define an error response class

    status_code = 400 # default to 'invalid usage'

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        return rv

def getLayerDataTypes(mapId, ctx):
    filename = os.path.join(
        ctx['dataRoot'], 'view', mapId, 'Layer_Data_Types.tab')
    fd = open(filename, 'rU')
    return csv.reader(fd, delimiter='\t'), fd

def getFirstAttribute(mapId, ctx):
    csv, fd = getLayerDataTypes(mapId, ctx)
    first = None
    for row in csv:
        if row[0] == 'FirstAttribute':
            first = row[1]
            break
    fd.close()
    return first

def getLayoutIndex(layoutName, mapId, ctx):
    filename = os.path.join(ctx['dataRoot'], 'view', mapId, 'layouts.tab')
    with open(filename, 'rU') as f:
        f = csv.reader(f, delimiter='\t')
        index = None
        for i, row in enumerate(f.__iter__()):
            if row[0] == layoutName:
                index = i
                break
        return index

def getMapMetaData(mapId, ctx):
    
    # Retrieve the meta data for this map
    dataFd = None
    filename = os.path.join(ctx['dataRoot'], 'view', mapId, 'mapMeta.json')
    try:
        dataFd = open(filename, 'r')
    except:
        return {}
    try:
        data = json.load(dataFd)
    except:
        raise ErrorResp('Could not convert json to python for ' + filename)

    dataFd.close()
    return data

def validateString(name, data, required=False):
    if required and name not in data:
        raise ErrorResp(name + ' parameter missing or malformed')
    if not isinstance(data[name], types.StringTypes):
        raise ErrorResp(name + ' parameter should be a string')

def validateMap(data, required):
    validateString('map', data, required)

def validateLayout(data, required):
    validateString('layout', data, required)

def validateEmail(data):
    if 'email' in data and not (isinstance(data['email'], types.StringTypes)
        or (isinstance(data['email'], list))):
        raise ErrorResp(
            'email parameter should be a string or list/array of strings')

def validateViewServer(data):
    if 'viewServer' not in data:
        return
    validateString('viewServer', data)
