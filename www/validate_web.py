
import os, json, types, re
from util_web import SuccessResp, ErrorResp

def _validateFileName (dirty, name):
    '''
    check to be sure this is a file-safe name without any problem characters
    Valid characters:
        a-z, A-Z, 0-9, dash (-), dot (.), underscore (_)
    All other characters are replaced with underscores.
    @param dirty: the string to check
    @param name: the data property name
    @return: nothing or raise an ErrorResp
    '''
    regex = r'[^A-Za-z0-9_\-\.].*'
    msg = name + ' parameter may only contain the characters:' + \
            ' a-z, A-Z, 0-9, dash (-), dot (.), underscore (_)'
    if name == 'map':
        msg += ', one slash (/)'
    search = re.search(regex, dirty)
    if not search == None:
        raise ErrorResp(msg)

def _validateStringChars(val, name):
    '''
    Look for any non-printable characters in a string value.
    @param  val: the string value
    @param name: the name of the parameter
    @return: nothing or raise an ErrorResp
    '''
    regex = r'[\x00-\x1f\x7f-\xff]'
    search = re.search(regex, val)
    if not search == None:
        raise ErrorResp(name +
            ' parameter should only contain printable characters')

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

def map(data, required):
    _validateString('map', data, required)

    # Is the name file-safe?
    val = data['map']
    slashCount = val.count('/')
    
    if slashCount > 1:
        raise ErrorResp('map IDs may not contain more than one slash')
    
    elif slashCount < 1:
        _validateFileName(val, 'map')
    
    else:  # one slash
        i = val.find('/')
        _validateFileName(val[0:i], 'map')
        _validateFileName(val[i+2:], 'map')

def layoutInputName(data, required):
    _validateString('layoutInputName', data, required, True)

def layout(data, required):
    _validateString('layout', data, required)

def authGroup(data):
    _validateString('authGroup', data)

def email(data):
    _validateString('email', data, False, True)

def viewServer(data):
    if 'viewServer' not in data:
        return
    _validateString('viewServer', data)
