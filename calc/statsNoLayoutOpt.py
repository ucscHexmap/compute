#! /usr/bin/env python2.7
'''
This is an optimized version of our pairwise attribute statistics.
Instead of using the lower level paralell processing of initiallizing n**2 classes
 it takes advantage of the parallel processing implemented in sklearn

 Notable changes to occur after testing passes:
      If a test fails and returns NA, we will not set that values to 1
       because a p-values of NA or 1 have very differnent meaning
'''
'''
 Notes on implementation:
  In order to take advantage of sklearn's parallel all-pairwise computation, and maintain
  the pairwise-complete observation of the statistical tests (i.e. nodes with Na in either of the
  attributes are not considered for the tests.), we must code Na's as appropriate real valued
  numbers.
  This only occurs within functions in this module and will not affect any other programs
  using this module.

  For binary and categorical data types -1 is used to represent a value of NA

  For continuous data types, the maximum float value is used. The argument for choosing this value
    is that it should not occur naturally because of the dangers of overflow.

  Those decisions can be easily changed by setting *NAN the globals below.
  ---------------
  Pvalue Adjustments are done in the write*() function
  ---------------
  dropQuantiles() function makes no sense in the context of rank sums test. Outliers are treated in the rank sums
   by a rank transform, and therefor you don't need to get rid of outliers that may affect the test. It is implemented
   here for reasurance that the statistical tests are producing the same numbers before changes.
'''
import pandas as pd
import numpy as np
import sklearn.metrics.pairwise as sklp
from scipy import stats
from leesL import getLayerIndex
import statsmodels.sandbox.stats.multicomp as multicomp
import math
import multiprocessing
#globals numbers used to represent NA values
FLOATNAN  = np.finfo(np.float64).max
BINCATNAN = -1

def filterNan(x,y):
    eitherNan = np.logical_or(np.isnan(x),np.isnan(y))
    x=x[~eitherNan]
    y=y[~eitherNan]
    return x,y

def contingencyTable(x,y):
    '''
    :param x: discrete numpy array
    :param y: discrete numpy array
    :return: a contingency table representing the co-occurence of discrete values,
             y is the column x is the row
    '''
    x_n = len(set(x))
    y_n = len(set(y))

    # a dict of combinations present and the indecies for which they occur
    groupDict = pd.DataFrame([x,y],index=[0,1]).transpose().groupby([0,1]).groups

    #intialize matrix that represents all all prosible combinations of the two discrete vars
    table = np.repeat(0,x_n*y_n).reshape(x_n,y_n)

    #fill in each combo that we have data for
    for key in groupDict.keys():
        #must modify the key to prevent off by one error when
        # accessing matrix
        modkey = tuple(map(lambda x: int(x)-1,key))

        table[modkey] = len(groupDict[key])

    return table

def binBinTest(x,y):
    #filter out bad values
    x,y = filterNan(x,y)
    #build contingency table
    table = contingencyTable(x,y)
    #if contingency table for binaries doesn't have this shape,
    # then there are no observations for one of the binary variables values
    # e.g. after Na's are filtered there are only 1's present in one of the attributes,
    # statistics can not accurately be computed
    if table.shape != (2,2):
        return np.NAN
    try:
        oddsratio, pValue = stats.fisher_exact(table)
    except ValueError:
        pValue = np.nan

    return pValue

def catBinOrCatCatTest(x,y):
    '''
    handles binary and categical or categorical ccategorical
    '''
    x,y = filterNan(x,y)
    #build contingency table
    table = contingencyTable(x,y)
    try:
        chi2, pValue, dof, expectedFreq = stats.chi2_contingency(table)
    except ValueError:
        pValue = np.nan

    return pValue

def contContTest(x,y):
    x,y = filterNan(x,y)
    try:
        correlation, pValue = stats.pearsonr(x,y)
    except ValueError:
        pValue = np.nan

    return pValue

def catContTest(catx, conty):

    catx, conty = filterNan(catx,conty)

    groups = pd.DataFrame([catx,conty]).transpose().groupby([0])

    samples = groups.aggregate(lambda x: list(x))[1].tolist()
    try:
        stat, pValue = stats.mstats.kruskalwallis(*samples)
    except ValueError:
        pValue = np.nan

    return pValue

def binContTest(binx, conty):
    '''

    @param binx: series or np.array representing binary data
    @param conty: series or np.array representing continuos data.
    @return: a pvalue calculated from scipy.ranksums
    '''
    binx, conty = filterNan(binx, conty)

    # Make groups according to binary stat test.
    groupDF = pd.DataFrame([binx, conty])
    groups = groupDF.transpose().groupby(groupDF.index[0])

    # Manipulate to format expected by stats.ranksums().
    two_samples = groups.aggregate(lambda x: list(x)).values

    # Compute stats.
    try:
        stat, pValue = stats.ranksums(*two_samples)
    except ValueError:
        pValue = np.nan
    except TypeError:
        # Happens when there are not two groups formed.
        pValue = np.nan

    return pValue

def read_matrices(projectDir):
    '''
    Puts the metadata matrices files in a list, to be used in
    utils.getAttributes()
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


def stitchTogether(biXbi, caXbi, biXco, coXco, caXco, caXca):
    '''
    this function takes the results from each of the pairwise
    computations and stiches them together into one data frame so they
    can be written out easily
    @param biXbi:
    @param caXbi:
    @param coXbi:
    @param coXco:
    @param caXco:
    @param caXca:
    @return:
    '''
    #stich together rows of individual datatypes
    bins = pd.concat([biXbi,caXbi,biXco.transpose()],axis=0)
    conts = pd.concat([coXco,biXco,caXco],axis=0)
    cats = pd.concat([caXca,caXbi,caXco],axis=1).transpose()

    return pd.concat([bins,conts,cats],axis=1)


def allbyallStatsNoLayout(attrDF, datatypeDict, n_jobs=12):
    '''
    @param projectDir:
    @param attrDF:
    @param attributeFileList:
    @param datatypeDict:
    @return:
    '''
    '''
    Computes all by all statistical tests for attributes
    @param projectDir:
    @param attributeFileList:
    @param datatypeDict:
    @return:
    '''

    # Separate attributes into data types.
    binAtts = attrDF[datatypeDict['bin']]
    binAtts = binAtts.fillna(BINCATNAN)

    catAtts = attrDF[datatypeDict['cat']]
    catAtts = catAtts.fillna(BINCATNAN)

    contAtts = attrDF[datatypeDict['cont']]
    contAtts = contAtts.fillna(FLOATNAN)

    # Each pair of data combos is done separately.
    biXbi = sklp.pairwise_distances(binAtts.transpose(),metric=binBinTest,n_jobs=n_jobs)
    biXbi = pd.DataFrame(biXbi,columns=datatypeDict['bin'],index=datatypeDict['bin'] )

    coXco = sklp.pairwise_distances(contAtts.transpose(),metric=contContTest,n_jobs=n_jobs)
    coXco = pd.DataFrame(coXco,columns=datatypeDict['cont'],index=datatypeDict['cont'] )

    caXca = sklp.pairwise_distances(catAtts.transpose(),metric=catBinOrCatCatTest,n_jobs=n_jobs)
    caXca = pd.DataFrame(caXca,columns=datatypeDict['cat'],index=datatypeDict['cat'] )

    caXbi = sklp.pairwise_distances(catAtts.transpose(),binAtts.transpose(),metric=catBinOrCatCatTest,n_jobs=n_jobs)
    caXbi = pd.DataFrame(caXbi,columns=datatypeDict['bin'],index=datatypeDict['cat'] )
    #
    caXco = sklp.pairwise_distances(catAtts.transpose(),contAtts.transpose(),metric=catContTest,n_jobs=n_jobs)
    caXco = pd.DataFrame(caXco,columns=datatypeDict['cont'],index=datatypeDict['cat'] )

    biXco = sklp.pairwise_distances(binAtts.transpose(),contAtts.transpose(),metric=binContTest,n_jobs=n_jobs)
    biXco = pd.DataFrame(biXco,columns=datatypeDict['cont'],index=datatypeDict['bin'] )

    return stitchTogether(biXbi, caXbi, biXco, coXco, caXco, caXca)


def writeToDirectoryStats(dirName, allbyall, layers):


    assert(dirName[-1] == '/')

    for column in allbyall.columns:
        #print getLayerIndex(column,layers)
        statsO = pd.DataFrame(index= allbyall.index)
        statsO[0] = allbyall[column] #uncorrected pvalues

        statsO = statsO.iloc[statsO.index!=column] #get rid of identity

        #run the adjusted pvalues
        reject, adjPvals, alphacSidak, alphacBonf = multicomp.multipletests(statsO[0].values, alpha=0.05, method='fdr_bh')
        reject, adjPvalsB, alphacSidak, alphacBonf = multicomp.multipletests(statsO[0].values, alpha=0.05, method='bonferroni')

        statsO[1] = adjPvals
        statsO[2] = adjPvalsB

        filename = 'stats_'+ getLayerIndex(column,layers)+ '.tab'

        statsO.to_csv(dirName+filename,sep='\t',header=None)


def callFunc(triplet):
    f= triplet[0]
    x =triplet[1]
    y =triplet[2]
    return f(x,y)


def enoughForParallelComp(N):
    ENOUGH = 500
    return N >= ENOUGH


def oneByAllStats(attrDF, datatypeDict, newAttr, newAttrDataType):
    """
    import pandas as pd
    import numpy as np
    attrDF = pd.read_table("/home/duncan/hex/compute/tests/out/stats/allAttributes.tab", index_col=0)
    datatypeDict = read_data_types("/home/duncan/hex/compute/tests/out/stats/")
    newAttr = attrDF[attrDF.columns[1]]
    newAttrDataType = "bin"
    :param attrDF: pandas dataframe, all attributes for a particular
    map.
    :param dataTypeDict: Datatype keys pointing to array of attrNames.
    :param newLayer: Must be parallel to attrDF,
    :param newLayerDataType:
    :return:
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

    # Fill with the Nan code (change this if you can!!!!!!!!!!!)
    #binAtts = binAtts.fillna(BINCATNAN)
    #catAtts = catAtts.fillna(BINCATNAN)
    #contAtts = contAtts.fillna(FLOATNAN)

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
        pool = multiprocessing.Pool(processes=5)
        pvalues = pd.Series(pool.map(callFunc, opPool))
        pool.close()
        pool.join()
    else:
        pvalues = pd.Series(map(callFunc, opPool))

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


def runAllbyAllForUI(dir, layers, attrDF, dataTypeDict):
    '''
    @param dir:
    @param layers:
    @param attrDF:
    @param dataTypeDict:
    @return:
    '''
    writeToDirectoryStats(
        dir,
        allbyallStatsNoLayout(attrDF, dataTypeDict),
        layers
    )

    return None