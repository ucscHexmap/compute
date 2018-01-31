"""Web utility for calculating spatial associations of a user
generated attribute to all other attributes on a map."""

import job
import leesL
import mapData
from typeTransforms import dictToPandasSeries

def preCalc(parms, ctx):
    userEmail = parms['email']
    return job.add(userEmail, "statsLayout", parms, ctx)


def calcMain(parms, ctx):
    # Pull out needed vars.
    mapName = parms["mapName"]
    focusAttr = parms["focusAttr"]
    layoutIndex = parms["layoutIndex"]
    # Get data ready for calculation.
    focusAttr = dictToPandasSeries(focusAttr)
    allBinAttrDF = mapData.getAllBinaryAttrs(mapName)
    xys = mapData.getXYs(mapName, layoutIndex)

    # Do calculation.
    leesLDF = leesL.oneByAll(
        allBinAttrDF,
        focusAttr,
        xys
    )

    webResponse = formatForWeb(leesLDF)

    return "Success", webResponse


def formatForWeb(leesLDF):
    """
    Turns a leesLDF dataframe into a list of lists in the format:

        [[ attributeId, leesL, Rank, Pearson Correlation],
        ...
        ]

    Nan values are replaced with string "nan"s.

    :param leesLDF: pandas DF with attributeName indices and columns
    leesL, Rank, correlation (in that order)
    :return: list of lists expected by TumorMap client.
    """
    leesLDF = leesLDF.fillna("nan")

    # Use pandas to produce desired format after some dataframe
    # manipulation.

    # Make new columns in correct order.
    newColName = "attrs"
    oldCols = leesLDF.columns
    newCols = [newColName]
    newCols.extend(oldCols)

    # Put a new column of row names/ attr names in the dataframe.
    leesLDF[newColName] = leesLDF.index

    # Order the columns.
    leesLDF = leesLDF[newCols]

    # Produces desired formatting.
    rowlist = leesLDF.as_matrix().tolist()

    return rowlist
