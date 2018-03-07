"""
Data access to already generated maps.
"""

import os
import pandas as pd
from utils import tabFilesToDF, readXYs


def readLayers(layerFile):
    return pd.read_csv(layerFile, sep='\t',index_col=0,header=None)


def getDataTypeDict(mapPath):
    """
    Mapping of which attributes are a given datatype for a map.
    @param mapPath: full path to a map directory
    @return: dict - {"bin": [attrId, attrId2, ...], "cat": [...].
    "cont": [...]}
    """
    #Abbreviations used in dataTypeDict
    dtypemap = {
        "Continuous": "cont",
        "Binary": "bin",
        "Categorical": "cat"
    }
    dataTypeFile = open(mapPath + '/Layer_Data_Types.tab')
    dataTypeDict = {}  # Returning this guy.
    # Handles format of the file, "firstAttribute" is passed.
    for line in dataTypeFile:
        line = line.strip().split('\t')
        found_datatype_row = line[0] in dtypemap
        if found_datatype_row:
            # Put it in the dictionary.
            try:
                dataTypeDict[dtypemap[line[0]]] = line[1:]
            except IndexError:
                dataTypeDict[dtypemap[line[0]]] = []

    return dataTypeDict


def getXYs(mapPath, layoutIndex):
    xysPath = os.path.join(
        mapPath,
        "xyPreSquiggle_" + str(layoutIndex) + ".tab"
    )
    return readXYs(xysPath)


def getAllAttributes(mapPath):
    """Returns a pandas dataframe of all attributes on a map."""
    attrFile = os.path.join(mapPath, "allAttributes.tab")

    try:
        attrDF = pd.read_table(attrFile, index_col=0)

    except IOError:
        # File is missing. Try and read the files an older way.
        matrix_files = getMatricesList(mapPath)
        attrDF = tabFilesToDF(matrix_files, mapPath)

    return attrDF


def getAllBinaryAttrs(mapPath):
    binAttrs = getDataTypeDict(mapPath)["bin"]
    binAttrDF = getAllAttributes(mapPath)[binAttrs]
    return binAttrDF


def getMatricesList(mapPath):
    '''
    Grab the list of matrix files from matrices.tab. Can be used with
    tabFilesToDF() to read all attributes for a map,
    use getAllAttributes instead.

    @param mapPath: the project directory
    @return: a list of strings, matrix file names ["matrix_0.tab", ...]
    '''
    matricesList = []
    with open(mapPath + '/matrices.tab') as filenames:
        for filename in filenames:
            fullpath = os.join(mapPath, filename.strip())
            matricesList.append(fullpath)

    return matricesList


def pathToMap(viewDir, mapName):
    return os.path.join(viewDir, mapName)
