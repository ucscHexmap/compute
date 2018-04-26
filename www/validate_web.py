
import os, json, types, re
from util_web import SuccessResp, ErrorResp

fileRegEx = r'[^A-Za-z0-9_\-\.].*'
fileSlashRegEx = r'[^A-Za-z0-9_\-\.\//].*'

def _dataIdOrUrl (dataId, url, data, required=False):
    if dataId in data:
        _validateString(dataId, data)
        _validatePathName(data[dataId], dataId)
    elif url in data:
        _validateString(url, data)
    elif required:
        raise ErrorResp(
            dataId + ' or ' + url + ' parameter missing or malformed')


def _validateFileName (dirty, name, allowSlash=False):
    '''
    check to be sure this is a file-safe name without any problem characters
    Valid characters:
        a-z, A-Z, 0-9, dash (-), dot (.), underscore (_)
    All other characters are replaced with underscores.
    @param dirty: the string to check
    @param name: the data property name
    @param allowSlash: allow a slash (/) in the string for paths
    @return: nothing or raise an ErrorResp
    '''
    msg = name + ' parameter may only contain the characters:' + \
            ' a-z, A-Z, 0-9, dash (-), dot (.), underscore (_)'
    if allowSlash:
        regex = fileSlashRegEx
        msg += ', slash (/)'
    else:
        regex = fileRegEx

    search = re.search(regex, dirty)
    if not search == None:
        raise ErrorResp(msg)


def _validateInteger (name, data, required=False):
    if name in data:
        try:
            val = int(data[name])
        except ValueError:
            raise ErrorResp(name + ' parameter must be an integer')
    elif required: # name is not in data
        raise ErrorResp(name + ' parameter missing or malformed')


def _validatePathName (dirty, name):
    _validateFileName (dirty, name, allowSlash=True)


def _validateString(name, data, required=False, arrayAllowed=False):
    '''
    Validate a string or an array of strings.
    @param         name: the name of the property in the data
    @param         data: the object in which the property resides
    @param     required: this property is required in the data, optional,
                         defaults to false
    @param arrayAllowed: an array of strings are allowed for this property,
                         optional, defaults to false
    @return: nothing or raise an ErrorResp
    '''
    if name in data:
        val = data[name]
        if isinstance(val, types.StringTypes):
            if len(val) < 1:
                raise ErrorResp(name +
                    ' parameter must have a string length greater than one')
            _validateStringChars(val, name)
        else:
        
            # This is not a string, but maybe an array.
            if arrayAllowed:
                if not isinstance(val, list):
                    raise ErrorResp(name +
                        ' parameter should be a string or an array of strings')
                
                # Check each string in the array
                for value in val:
                    if not isinstance(value, types.StringTypes):
                        raise ErrorResp(name +
                            ' parameter should be a string or an array of strings')
                    _validateStringChars(value, name)
            else:
                raise ErrorResp(name + ' parameter should be a string')

    elif required: # name is not in data
        raise ErrorResp(name + ' parameter missing or malformed')


def _validateStringChars(val, name):
    '''
    Look for any non-printable characters in a string value, non-printables are
    ascii decimal codes 0-31 and 127-255.
    @param  val: the string value
    @param name: the name of the parameter
    @return: nothing or raise an ErrorResp
    '''
    regex = r'[\x00-\x1f\x7f-\xff]'
    search = re.search(regex, val)
    if not search == None:
        raise ErrorResp(name +
            ' parameter should only contain printable characters')


def attributes(data, required=False):
    _validateString('attributes', data, required, arrayAllowed=True)


def authGroup(data):
    _validateString('authGroup', data)


def cleanFileName (dirty):

    # Make a directory or file name out of some string
    # Valid characters:
    #     a-z, A-Z, 0-9, dash (-), dot (.), underscore (_)
    # All other characters are replaced with underscores.

    if not dirty:
        return None
    
    clean = ''
    if not re.search(fileRegEx, dirty) == None:
        for i in range(0, len(dirty)):
            if re.search(fileRegEx, dirty[i]) == None:
                clean += dirty[i]
            else:
                clean += '_'

    return clean


def colorAttribute (data, required=False):
    _dataIdOrUrl('colorAttributeDataId', 'colorAttributeUrl', data, required)


def email(data):
    _validateString('email', data, False, True)


def layout(data, required=False):
    _validateString('layout', data, required)


def layoutInput (data, required=False):
    _dataIdOrUrl('layoutInputDataId', 'layoutInputUrl', data, required)


def layoutInputName(data, required):
    _validateString('layoutInputName', data, required, True)


def map(data, required):
    _validateString('map', data, required)

    # Is the name file-safe?
    val = data['map']
    slashCount = val.count('/')
    
    if slashCount > 1:
        raise ErrorResp('map IDs may not contain more than one slash')
    
    else:
        _validateFileName(val, 'map', allowSlash=True)


def neighborCount (data):
    name = 'neighborCount'
    _validateInteger (name, data)
    if name in data:
        if data[name] < 1 or data[name] > 30:
            raise ErrorResp('neighborCount parameter must be within the range, 1-30')


def nodes(data, required=False):
    _validateString('nodes', data, required, arrayAllowed=True)


def viewServer(data):
    if 'viewServer' not in data:
        return
    _validateString('viewServer', data)
