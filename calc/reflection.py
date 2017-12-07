#!/usr/bin/env python2.7
import pandas as pd
import os


def reflection(parm):
    '''
    Runs the "reflection" pipeline.
    :param parm: {
                  "datapath": relfection_data_file_name
                  "featOrSamp" : 'sample' or 'feature'
                  "node_ids" : [ "id1",...,"idn" ]
                  "rankCategories" t/f for ordinal calculation.
                  "n" : number of "high" and "low" if ordinal calc.
                  ""dataType": one of 'mRNA', 'CNV', 'miRNA',
                    'Methylation', 'RPPA'. Specifiest the type of score
                    calculation
                  }
    :return: pandas Series, int.
    '''

    fpath = str(parm['datapath'])
    nodeIds = parm['nodeIds']
    startingFromRows = parm["featOrSamp"] == "feature"
    dataType = parm["dataType"]
    ordinalRequested = parm["rankCategories"]

    if not os.path.isfile(fpath):
        raise IOError(fpath + " data for reflection not found")

    # feature X sample matrix being used for reflection transform.
    reflectionDF = pd.read_hdf(fpath)

    if startingFromRows:
        reflectionDF = reflectionDF.transpose()

    # Discard any nodes not in the reflection matrix.
    nodeIds = filterNodeIds(nodeIds, reflectionDF.columns)
    nNodesReflected = len(nodeIds)

    scoreCalculator = getScoreCalculator(dataType)

    reflectionScores = scoreCalculator(reflectionDF, nodeIds)

    if ordinalRequested:
        topBottomBinSize = parm["n"]
        reflectionScores = ordinalTransform(
            reflectionScores,
            topBottomBinSize
        )

    return reflectionScores, nNodesReflected


def getScoreCalculator(dataType):
    return {
        'mRNA': tStatCalc,
        'CNV' : average,
        'miRNA': tStatCalc,
        'RPPA': tStatCalc,
        'Methylation': tStatCalc
    }[dataType]


def ordinalTransform(df, topN):
    '''
    :param df: single column pandas Dataframe
    :return: pandas Series
    '''
    nanRows = df.isnull().values
    nrows = df.shape[0]
    df = df.sort_values(ascending=False)

    df.iloc[0:(topN)] = "high"
    df.iloc[topN:-topN] = "middle"
    df.iloc[nrows-topN:nrows] = "low"
    df.iloc[nanRows] = "NAN"

    return pd.Series(df)


def average(df, nodeIds):
    return df[nodeIds].mean(axis=1)


def tStatCalc(df, nodeIds):
    rowmu = df.mean(axis=1)
    rowstd = df.std(axis=1)
    tStats = ((df[nodeIds].mean(axis=1) - rowmu) / rowstd)
    return tStats


def filterNodeIds(nodeIds, nodesInReflection):
    filteredNodes = list(
        set(nodeIds).intersection(set(nodesInReflection)))
    empty = (len(filteredNodes) == 0)
    if (empty):
        raise ValueError("None of the nodes were in the data matrix.")
    return filteredNodes