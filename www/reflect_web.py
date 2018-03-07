
from reflection import reflection
from util_web import getProjMajor, getProjMinor, mkTempFile, tmpDir
from util_web import ErrorResp

import pickle
import os
import json
import job


def preCalc(parms, ctx):
    userEmail = parms['email']
    return job.add(userEmail, "reflect", parms, ctx)


def calcMain(parms, ctx):
    dataType = parms["dataType"]
    selectionName = parms["dynamicAttrName"]

    reflectionParms = getReflectParmameters(parms)

    reflectionScores, nNodes = reflection(reflectionParms)

    attrName = reflectionAttrName(selectionName, dataType)

    reflectionScores = formatForWeb(reflectionScores, attrName)

    # Write the response out as a pickle.
    tmpFilePath = mkTempFile()
    attrId = reflectionAttrId(tmpFilePath)
    pickle.dump(reflectionScores, open(tmpFilePath, "wb"))

    retrievalUrl = getRetrievalUrl(attrId)
    return "Success", {"url": retrievalUrl, "nNodes": nNodes}


def getReflectionAttr(attrId):
    """Grabs a reflection attr with an attribute Id."""
    filepath = os.path.join(tmpDir(), attrId)
    with open(filepath, 'rb') as reflectData:
        reflectDict = pickle.load(reflectData)

    return reflectDict


def getReflectionMetadata(mapId):
    """Get data needed for client have reflection available."""
    majorId, minorId = getProjMajor(mapId), getProjMinor(mapId)
    reflectJson = getReflectJson()
    dataTypes = getDataTypes(majorId, reflectJson)

    toMapIds = getToMapIds(mapId, reflectJson)
    metadata = {
        "dataTypes": dataTypes,
        "toMapIds": toMapIds
    }
    if toMapIds is None and dataTypes is None:
        raise ErrorResp(
            "Reflection meta data for this map is not found.",
            204
        )

    return metadata


def formatForWeb(reflectionScores, attrName):
    dictFormat = {}
    dictFormat[attrName] = reflectionScores.tolist()
    dictFormat["sampleID"] = reflectionScores.index.tolist()
    return dictFormat


def getReflectParmameters(parms):
    """Make the parameter dict ready for reflection function."""
    reflectJson = getReflectJson()
    dataType = parms["dataType"]
    mapId = parms["map"]
    projMajor, projMinor = getProjMajor(mapId), getProjMinor(mapId)

    # Set parameter dictionary with other needed variables.
    parms["calcType"] = getCalcType(projMajor, dataType, reflectJson)
    parms["featOrSamp"] = getFeatOrSamp(mapId, reflectJson)
    parms["n"] = getTopBinSize(mapId, reflectJson)
    parms["datapath"] = getDataFilePath(
        projMajor,
        dataType,
        reflectJson
    )

    return parms


def getRetrievalUrl(attrId):
    """The URL to query the server for to retrieve data."""
    url = "/reflect/attrId/" + attrId
    return url


def reflectionAttrName(selectionName, dataType):
    return selectionName + "_" + dataType + "_Reflect"


def reflectionAttrId(filepath):
    """
    :param filepath:
    :return: The temp file name.
    """
    return filepath.split("/")[-1]


def getToMapIds(mapId, reflectJson):
    majorId, minorId = getProjMajor(mapId), getProjMinor(mapId)
    try:
        toMapIds = reflectJson[majorId][minorId]["toMapIds"]
    except KeyError:
        toMapIds = None
    return toMapIds


def getDataTypes(majorId, reflectJson):
    try:
        datatypes = reflectJson[majorId]["dataTypesToCalcType"].keys()
    except KeyError:
        datatypes = None
    return datatypes


def getFeatOrSamp(mapId, reflectJson):
    majorId, minorId = getProjMajor(mapId), getProjMinor(mapId)
    return reflectJson[majorId][minorId]["featOrSamp"]


def getTopBinSize(mapId, reflectJson):
    majorId, minorId = getProjMajor(mapId), getProjMinor(mapId)
    defaultBinSize = 150
    binSize = defaultBinSize
    try:
        binSize = reflectJson[majorId][minorId]["n"]
    except KeyError:
        pass

    return binSize


def getReflectJson():
    try:
        hubPath = os.environ.get("HUB_PATH")
        reflectDbPath = os.path.join(
            hubPath,
            "..",
            "computeDb/reflection.json"
        )
        reflectJson = json.load(open(reflectDbPath, "r"))
    except IOError:
        raise IOError(
            "Reflection MetaData is missing from the server."
        )

    return reflectJson


def getCalcType(projMajor, dataType, reflectJson):
    try:
        cType = reflectJson[projMajor]["dataTypesToCalcType"][dataType]
    except KeyError:
        cType = None
    return cType


def getDataFilePath(projMajor, dataType, reflectJson):
    dataRoot = os.environ.get('DATA_ROOT')

    filepath = \
        os.path.join(
            dataRoot,
            "featureSpace",
            projMajor,
            "reflection",
            reflectJson[projMajor]["dataTypesToFileName"][dataType]
        )

    return filepath