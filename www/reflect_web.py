
from reflection import reflection
from util_web import getProjMajor, getProjMinor, mkTempFile, tmpDir
import pickle
import os
import json
import job


def preCalc(parms, ctx):
    userEmail = parms['email']
    return job.add(userEmail, "reflect", parms, ctx)


def calcMain(parms, ctx):
    dataType = parms["dataType"]
    selectionName = parms["selectionSelected"]

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


def getReflectionMetaData(majorId, minorId):
    dataTypes = getDataTypes(majorId)
    toMapIds = getToMapIds(majorId, minorId)
    metadata = {
        "dataTypes": dataTypes,
        "toMapIds": toMapIds
    }
    return metadata


def formatForWeb(reflectionScores, attrName):
    dictFormat = {}
    dictFormat[attrName] = reflectionScores.tolist()
    dictFormat["sampleID"] = reflectionScores.index.tolist()
    return dictFormat


def getReflectParmameters(parms):
    """Make the parameter dict ready for reflection function."""
    dataType = parms["dataType"]
    mapId = parms["mapId"]
    projMajor = getProjMajor(mapId)
    projMinor = getProjMinor(mapId)

    parms["calcType"] = getCalcType(projMajor, dataType)
    parms["datapath"]  = getDataFilePath(projMajor, dataType)
    parms["featOrSamp"] = getFeatOrSamp(projMajor, projMinor)
    parms["n"] = getTopBinSize(projMajor, projMinor)

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


def getToMapIds(majorId, minorId):
    reflectJson = getReflectJson()
    return reflectJson[majorId][minorId]["toMapIds"]


def getDataTypes(majorId):
    reflectJson = getReflectJson()
    return reflectJson[majorId]["dataTypesToCalcType"].keys()


def getFeatOrSamp(majorId, minorId):
    reflectJson = getReflectJson()
    return reflectJson[majorId][minorId]["featOrSamp"]


def getTopBinSize(majorId, minorId):
    reflectJson = getReflectJson()
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
        raise IOError(str(reflectDbPath))

    return reflectJson


def getCalcType(projMajor, dataType):
    config = getReflectJson()
    return config[projMajor]["dataTypesToCalcType"][dataType]


def getDataFilePath(projMajor, dataType):
    dataRoot = os.environ.get('DATA_ROOT')
    config = getReflectJson()

    filepath = \
        os.path.join(
            dataRoot,
            "featureSpace",
            projMajor,
            "reflection",
            config[projMajor]["dataTypesToFileName"][dataType]
        )

    return filepath