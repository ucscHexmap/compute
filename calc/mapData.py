"""
Data access to already generated maps.
"""

import os
import pandas as pd
from utils import tabFilesToDF, readXYs

def readLayers(layerFile):
    return pd.read_csv(layerFile, sep='\t',index_col=0,header=None)


def getDataTypeDict(mapName):
    """
    Returns { "bin": [attrName,...], "cat": [...], "cont":[...]}
      which gives the data type distinctions for all attributes in a
       map.
    """
    projectDir = os.path.join(
        os.environ.get("DATA_ROOT"),
        "view",
        mapName,
    )
    return read_data_types(projectDir)


def getXYs(mapName, layoutIndex):
    projectDir = pathToMap(mapName)
    xysPath = os.path.join(
        projectDir,
        "xyPreSquiggle_" + str(layoutIndex) + ".tab"
    )
    return readXYs(xysPath)


def getAllAttributes(mapName):
    """Returns a pandas dataframe of all attributes on a map."""
    projectDir = pathToMap(mapName)
    attrFile = os.path.join(projectDir, "allAttributes.tab")

    try:
        attrDF = pd.read_table(attrFile, index_col=0)

    except IOError:
        # Try and read the files an older way.
        matrix_files = read_matrices(projectDir)
        attrDF = tabFilesToDF(matrix_files, projectDir)

    return attrDF


def getAllBinaryAttrs(mapName):
    binAttrs = getDataTypeDict(mapName)["bin"]
    binAttrDF = getAllAttributes(mapName)[binAttrs]
    return binAttrDF


def read_matrices(projectDir):
    '''
    Puts the metadata matrices files in a list, to be used in layout.getAttributes()
     and is dependent upon the matrix file being in proper format.
    @param projectDir: the project directory
    @return: a list of the matrix file names
    '''
    matlist = []
    #grab each name
    for line in open(projectDir + '/matrices.tab'):
        matlist.append(projectDir + '/' + line.strip())

    return matlist


def read_data_types(projectDir):
    '''

    @param projectDir:
    @return:
    '''
    #mapping from what is in the file to abbreviations used in dataTypeDict
    dtypemap = {"Continuous":"cont","Binary":"bin","Categorical":"cat"}
    dtfin = open(projectDir + '/Layer_Data_Types.tab')
    dataTypeDict = {}
    for line in dtfin:
        line = line.strip().split('\t')
        #if we recognize the category
        if line[0] in dtypemap:
            try:
                dataTypeDict[dtypemap[line[0]]] = line[1:]
            except IndexError:
                dataTypeDict[dtypemap[line[0]]] = []

    return dataTypeDict


def pathToMap(mapName):
    return os.path.join(
        os.environ.get("DATA_ROOT"),
        "view",
        mapName
    )
