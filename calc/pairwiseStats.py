#! /usr/bin/env python2.7
"""
Functions for the pairwise attribute stat tests done by tumormap.
"""
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.sandbox.stats.multicomp as multicomp
import multiprocessing

def oneByAllStats(attrDF, datatypeDict, newAttr, newAttrDataType):
    """
    Performs one by all stats on newAttr to attrDF.
    :param attrDF: pandas dataframe, all attributes for a particular
    map.
    :param dataTypeDict: Datatype keys pointing to array of attrNames.
    :param newAttr: Pandas series
    :param newAttrDataType: One of ["bin", "cat", "cont"]
    :return: DataFrame with Single test pvalue BHFDR and bonferonni
    columns.
    """
    # Filter down to only nodes that the new attr has.
    attrDF = attrDF.loc[newAttr.index]

    # Gather attribute names.
    # This var contains the ordering that needs to be maintained
    # in the processing pool.
    attrNames = []
    attrNames.extend(attrDF[datatypeDict['bin']].columns)
    attrNames.extend(attrDF[datatypeDict['cat']].columns)
    attrNames.extend(attrDF[datatypeDict['cont']].columns)
    attrNames = pd.Series(attrNames)

    # Separate the attributes out into data types.
    binAtts = attrDF[datatypeDict['bin']]
    catAtts = attrDF[datatypeDict['cat']]
    contAtts = attrDF[datatypeDict['cont']]

    # Format DFs to create the pool for processing.
    binAtts = binAtts.transpose().as_matrix()
    catAtts = catAtts.transpose().as_matrix()
    contAtts = contAtts.transpose().as_matrix()
    attr = newAttr.as_matrix()

    # Make the pool of operations for the new attribute depending on
    # the dataType. The idea here is create a pool of triplets.
    # We map a wrapper function through this pool that calls the
    # function (first triplet) with the two args (2nd and 3rd triplet).
    # Again, the ordering of the pool needs to be kept the same as the
    # columnNames var, namely bin-cat-cont.
    if newAttrDataType == "bin":
        opPool = [(binBinTest, attr, np.array(x)) for x in binAtts]
        opPool.extend([(catBinOrCatCatTest, x, attr) for x in catAtts])
        opPool.extend([(binContTest, attr, x) for x in contAtts])

    elif newAttrDataType == "cat":
        opPool = [(catBinOrCatCatTest, attr, x) for x in binAtts]
        opPool.extend([(catBinOrCatCatTest, attr, x) for x in catAtts])
        opPool.extend([(catContTest, attr, x) for x in contAtts])

    elif newAttrDataType == "cont":
        opPool = [(binContTest, x, attr) for x in binAtts]
        opPool.extend([(catContTest, x, attr) for x in catAtts])
        opPool.extend([(contContTest, x, attr) for x in contAtts])

    else:
        raise ValueError("Invalid datatype: " + newAttrDataType)

    # Execute computations. Go parallel if there are many attributes
    # to process.
    if enoughForParallelComp(len(attrNames)):
        pool = multiprocessing.Pool(processes=10)
        pvalues = pd.Series(pool.map(callFunction, opPool))
        pool.close()
        pool.join()
    else:
        pvalues = pd.Series(map(callFunction, opPool))

    # Filter out pvalues with NaN because they futz with the
    # pvalue adjustments.
    validIndecies = np.isfinite(pvalues).values
    filteredps = pvalues[validIndecies].as_matrix()
    filteredNames = attrNames[validIndecies]

    # Run the adjustments.
    FdrBHs = multicomp.multipletests(
        filteredps,
        alpha=0.05,
        method='fdr_bh'
    )[1]
    bonferonnis = multicomp.multipletests(
        filteredps,
        alpha=0.05,
        method='bonferroni'
    )[1]

    # Construct DataFrame and return.
    colnames = [
        "single test pvalue",
        "FDRBH",
        "bonferonnis"
    ]
    dfDict = dict(
        zip(
            colnames,
            [filteredps, FdrBHs, bonferonnis],
        )
    )
    pValueDF = pd.DataFrame(
        dfDict,
        index=filteredNames,
        columns=colnames
    )

    return pValueDF


def enoughForParallelComp(N):
    ENOUGH = 500
    return N >= ENOUGH


def binBinTest(x,y):
    try:
        x,y = filterNan(x,y)
        table = contingencyTable(x,y)
        if table.shape != (2, 2):
            # Can't compute pvalue without the correct number of
            # categories.
            raise ValueError

        oddsratio, pValue = stats.fisher_exact(table)
    except ValueError:
        pValue = np.nan

    return pValue


def catBinOrCatCatTest(x,y):
    try:
        x,y = filterNan(x,y)
        table = contingencyTable(x,y)
        chi2, pValue, dof, expectedFreq = stats.chi2_contingency(table)
    except ValueError:
        pValue = np.nan

    return pValue


def contContTest(x,y):
    try:
        x,y = filterNan(x, y)
        correlation, pValue = stats.pearsonr(x, y)

    except ValueError:
        pValue = np.nan

    return pValue


def catContTest(catx, conty):
    try:
        catx, conty = filterNan(catx, conty)

        groups = pd.DataFrame([catx, conty]).transpose().groupby([0])

        samples = groups.aggregate(lambda x: list(x))[1].tolist()

        stat, pValue = stats.mstats.kruskalwallis(*samples)

    except ValueError:
        pValue = np.nan

    return pValue


def binContTest(binx, conty):
    try:
        binx, conty = filterNan(binx, conty)

        # Make groups according to binary stat test.
        groupDF = pd.DataFrame([binx, conty])
        groups = groupDF.transpose().groupby(groupDF.index[0])

        # Make sure there are 2 groups from the binary variable.
        if len(groups) != 2:
            raise ValueError

        # Manipulate to format expected of scipy.stats.ranksums().
        two_samples = groups.aggregate(lambda x: list(x)).values
        sample1 = two_samples[0][0]
        sample2 = two_samples[1][0]

        stat, pValue = stats.ranksums(sample1, sample2)

    except ValueError:
        pValue = np.nan

    return pValue


def contingencyTable(x,y):
    """
    Make a contingency table.
    :param x: discrete numpy array
    :param y: discrete numpy array
    :return: 2d numpy array: y's are the columns x's are the rows
    """
    x_n = len(set(x))
    y_n = len(set(y))
    x = stats.rankdata(x, "dense")
    y = stats.rankdata(y, "dense")
    # Variable combinations pointing to indecies where they occur.
    groupDict = pd.DataFrame([x,y],index=[0,1]).transpose().groupby([0,1]).groups

    # Represents all combinations of variables.
    table = np.repeat(0, x_n*y_n).reshape(x_n, y_n)

    # Fill each variable combo there is data for.
    for key in groupDict.keys():
        # Key is modified to prevent off by one error when accessing
        modkey = tuple(map(lambda x: int(x)-1, key))

        table[modkey] = len(groupDict[key])

    return table


def filterNan(x,y):
    """Indecies where either x or y are NA
    are removed. x , y must be same length."""
    eitherNan = np.logical_or(np.isnan(x),np.isnan(y))
    x = x[~eitherNan]
    y = y[~eitherNan]
    if len(x) == 0:
        raise ValueError("No matching values were found.")

    return x, y


def callFunction(triplet):
    f = triplet[0]
    x = triplet[1]
    y = triplet[2]
    return f(x, y)