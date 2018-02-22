#! /usr/bin/env python2.7
'''
Tumor Map specific calculations of spatial association (SA).
The spatial smoothing scalar is used for a notion of density
for each attribute-layout pair. And lees L measure for bivariate
spatial association is used as an attribute-attribute value ranking.

Uses leesL stats_matrix for computations.
'''
import math
import pandas as pd
import sklearn.metrics.pairwise as sklp
from scipy import stats
import numpy as np
import scipy.spatial.distance as dist
import leesL

def density(allAtts, datatypes, xys, n_jobs=1):
    '''
    Calculate the density for a set of attributes.
    Uses euclidean similarity of xys as spatial weight matrix.
     new spatial weight matrix is calculated for every attribute based on the
     nodes that it has missing values for. Because attributes often come in
     groups, and the profile of missing values is dependent on those groups,
     instead of calculating a spatial weight matrix for each attribute we can
     calculate one for each missing data profile. This is done by creating an
     all by all distance matrix of the missing value profiles, and using it to
     determine what attributes have the same profile, i.e. a distance of 0.

    :param allAtts: the entire attribute matrix (pandas dataframe) , density
    calculated for each column
    :param datatypes: a datatype dict, {'bin': [],'cont':[],'cat': []}
    :param xys: a x-y (column) by nodeId position matrix (pandas dataframe)
    :param n_jobs: number of jobs in parralell processing
    :return: a pandas Series of attributes paired with their density values.
    '''

    #parallel arrays to be stuffed with density values for each attribute
    attrNames = []
    densities = []

    # Subset the attributes to the xy positions for this map.
    allAtts = allAtts.loc[xys.index]

    # Constants for determining whether there is enough data to calculate
    # density
    minNeeded = 5
    percentNeeded = .025
    minNodes = math.ceil(len(xys.index) * percentNeeded) + minNeeded


    # Datatypes are cased out.
    for type_ in datatypes.keys():
        # Continuous and binary types have the same calculation
        if type_ != 'cat' and len(datatypes[type_]) > 1:
            # Subset the attributes to the specific type
            attrDtypeSubset = allAtts[datatypes[type_]]

            # Make a distance matrix of the NaN profiles for each attribute.
            distMat = sklp.pairwise_distances(
                         attrDtypeSubset.isnull().transpose(),
                         metric='hamming',
                         n_jobs=n_jobs
                      )
            # The distance matrix allows finding
            # of attributes with the same NaN profile.
            # We can calculate the density of those groups together,
            # speeding up performance.

            # Keeps track of the attributes that density hasn't been
            # calculated for.
            indecies_to_check = range(len(datatypes[type_]))

            # Loop until there are no more.
            while(len(indecies_to_check)):

                index_ = indecies_to_check[0]

                # Store the distances from that attribute.
                sims = distMat[index_,]

                # Find attributes that have the same NaN profile.
                mask = (sims == 0)

                # Put the attribute names that are exactly similar into the
                # returning structure
                attrNames.extend(attrDtypeSubset.columns[mask])
                # Drop the Na's in those attributes
                datMat = attrDtypeSubset[attrDtypeSubset.columns[mask]].dropna()
                # Z-score transformation to prepare for density calculation
                datMat = ztransDF(datMat)


                # Pass if the map doesn't have has enough data.
                if datMat.shape[0] < minNodes: #
                    densities.extend(np.repeat(np.NAN, mask.sum()))
                    print 'attributes ' + str(attrDtypeSubset.columns[mask])\
                          + ' had no values for this xy position set'
                else:
                    # The diagonal of the leesL calculation is the SSS
                    densities.extend(
                        leesL.L(
                            datMat,
                            spatialWieghtMatrix(xys.loc[datMat.index])
                        ).diagonal()
                    )

                # Remove attributes that we have calculated density for.
                for colnum in np.where(sims == 0)[0]:
                    indecies_to_check.remove(colnum)

        #deal with categoricals
        if type_ == 'cat' and len(datatypes[type_]) > 0:
            attrDtypeSubset = allAtts[datatypes[type_]]

            for attr in attrDtypeSubset.columns:
                #expand our categorical vector to dummy variables
                datMat = pd.get_dummies(attrDtypeSubset[attr].dropna()).apply(pd.to_numeric)

                nNodes = datMat.sum().sum()
                #in case we lost any categories for the map we are looking at
                datMat = datMat[datMat.columns[datMat.sum() != 0]]
                datMat = ztransDF(datMat)

                #make sure there is enough data to calculate density
                if nNodes < minNodes:
                    print 'attribute ' + attr + ' didn\'t have enough values for this xy position set'
                    densities.append(np.NAN)
                else:
                    densities.append(
                        catSSS(
                            leesL.L(
                                datMat,
                                spatialWieghtMatrix(
                                    xys.loc[datMat.index]
                                ),
                            )
                        )
                    )

                attrNames.append(attr)

    return pd.Series(densities, index=attrNames)


def pairwiseAssociations(xys, binAttrDF):
    attrs = attrPreProcessing(xys, binAttrDF)
    spatialMatrix = spatialWieghtMatrix(xys)
    return leesL.L(attrs, spatialMatrix)


def oneByAll(allBinAttrDF, focusAttr, xys, n_jobs=1):
    """
    Perform 1 by all spatial association.
    :param allBinAttrDF: pandas dataframe of binary attributes
    :param focusAttr: pandas series of single binary attribute
    :param n_jobs: Number of jobs used in parallel processing of
    pearson correlations.
    :return: pandas dataframe with 3 columns, [leesL, Ranks, Pearson]
      and rows with the binary attributes in allBinAttrDF.
    """
    allBinAttrDF = attrPreProcessing(xys, allBinAttrDF)
    focusAttr = attrPreProcessing(xys, focusAttr)

    inCommon = set(focusAttr.index).intersection(allBinAttrDF.index)
    # Pearson correlation of all attributes is calculated for comparison

    pearsonD = sklp.pairwise_distances(
        focusAttr.loc[inCommon].values.reshape(-1, 1).transpose(),
        allBinAttrDF.loc[inCommon].transpose(),
        metric='correlation',
        n_jobs=n_jobs
    )[0,:]

    pearsonSim = 1 - pearsonD

    # Lees L vector
    leesLV = leesL.statistic_matrix(
        focusAttr,
        spatialWieghtMatrix(xys),
        allBinAttrDF
    )

    ranks = stats.rankdata(np.abs(leesLV), method='average')
    normalizedRank = 1 - (ranks / len(leesLV))

    columnNames = ["leesL", "Ranks", "Pearson"]

    dataDict = dict(
        zip(columnNames, [leesLV, normalizedRank, pearsonSim])
    )

    outDF = pd.DataFrame(
        dataDict,
        index=allBinAttrDF.columns,
    )

    # Make ordering correct.
    outDF = outDF[columnNames]

    return outDF


def attrPreProcessing(xys, attrDF):
    '''
    preproccesssing pipeline for doing leesL bivariate association
    @param attrDF:  metadata matrix, rows sample names
    @param xys:     the xy positions in the type provided by readXYs
    @return:        a new attributeDF with the preprocessing run
    '''
    #first subset the attribute matrix down to samples/nodes that are on the map
    attrOnMap = attrDF.loc[xys.index]

    #we treat missing data by first z scoring, then setting NA's to 0, order here matters
    attrOnMap = ztransDF(attrOnMap)
    attrOnMap.fillna(0, inplace=True)
    return attrOnMap


def catSSS(catLee):
    '''
    :param catLee: the LeesL matrix from a single categorical variable that has been expanded
                           into dummy variables, i.e. 3 categories from 1 vector being expanded to 3 binary vectors

                           The most dense categoical should have each of its categories
                             dense and also have each category well separated.

                           The diagonal of the lees L of the catLee describes the density for each
                           individual category. The off diagonal describes how much each category is
                           separated in space.

                           This metric combines on and off diagonal components by taking on_average - off_average

    :return: a function that creates a lees L estimate for a categorical variable
    '''

    #below we are twice over counting (matrix is symetric) but also twice over dividing, so that's not a mistake

    #         average of on_diagonal                           average of off diagonal
    return (catLee.trace() / catLee.shape[0]) - ((catLee.sum() - catLee.trace())/ (catLee.shape[1]**2 - catLee.shape[1]))


def spatialWieghtMatrix(xys):
    '''
    :param xys: x-y positions for nodes on the map
    :return: col X col inverse euclidean distance matrix,
    row normalized to sum to 1.
    '''
    invDist = inverseEucDistance(xys)

    # Self comparisons to 0
    notZd = pd.DataFrame(invDist,index=xys.index,columns=xys.index)

    return (notZd / notZd.sum(axis=1))


def inverseEucDistance(xys):

    distmat = dist.squareform(dist.pdist(xys,'euclidean'))
    return 1 / (1 + distmat)


def ztransDF(df):
    '''
    :param df: pandas structure, series or data frame
    :return: z-score normalized version of df.
    '''
    return ((df - df.mean(axis=0)) / df.std(axis=0, ddof=0))


def rowNormalize(spatialWeightMatrix):
    return spatialWeightMatrix / spatialWeightMatrix.sum(axis=1)


