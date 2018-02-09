"""Web utility for calculating statistical associations of a user
generated attribute to all other attributes on a map."""

import job
import pairwiseStats as stats
from typeTransforms import dictToPandasSeries
from mapData import getDataTypeDict, getAllAttributes

def preCalc(parms, ctx):
    userEmail = parms['email']
    return job.add(userEmail, "statsNoLayout", parms, ctx)


def calcMain(parms, ctx):
    # Pull out needed vars.
    mapName = parms["mapName"]
    focusAttr = parms["focusAttr"]
    focusAttrDatatype = parms["focusAttrDatatype"]

    # Get data ready for calculation.
    focusAttr = dictToPandasSeries(focusAttr)
    allAttrDF = getAllAttributes(mapName)
    datatypeDict = getDataTypeDict(mapName)

    # Do calculation.
    pvalueDF = stats.oneByAllStats(
        allAttrDF,
        datatypeDict,
        focusAttr,
        focusAttrDatatype
    )

    webResponse = formatForWeb(pvalueDF)

    return "Success", webResponse


def formatForWeb(pvalueDF):
    """
    Turns a pvalue dataframe into a list of lists in the format:

        [[ attributeId, single-test pvalue, BHFDR, bonefonni],
        ...
        ]

    Nan values are replaced with string "nan"s.

    :param pvalueDF: pandas DF with attributeName indices and columns
    single-test pvalue, BHFDR, bonefonni (in that order)
    :return: list of lists expected by TumorMap client.
    """
    pvalueDF = pvalueDF.fillna("nan")

    # Use pandas to produce desired format after some dataframe
    # manipulation.

    # Make new columns in correct order.
    newColName = "attrs"
    oldCols = pvalueDF.columns
    newCols = [newColName]
    newCols.extend(oldCols)

    # Put a new column of row names/ attr names in the dataframe.
    pvalueDF[newColName] = pvalueDF.index

    # Orders the columns properly.
    pvalueDF = pvalueDF[newCols]

    # Produces desired formatting.
    rowlist = pvalueDF.as_matrix().tolist()

    return rowlist


