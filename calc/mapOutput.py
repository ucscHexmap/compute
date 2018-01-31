
import pandas as pd
import numpy as np
from utils import sigDigs
from utils import truncateNP
from scipy import stats

def writeDummyLayersTab(
        layer_files,
        layers,
        attributeDF,
        datatypes,
        nlayouts,
        directory):
    """
    Writes out an empty layers.tab to the directory so the UI
     will work while density is being calculated
    @param layer_files:
    @param layers:
    @param attributeDF:
    @param datatypes:
    @param nlayouts:
    @return:
    """
    layer_files = trimLayerFiles(layer_files)

    layersTab = pd.DataFrame(index=layer_files.keys())

    #second column is the name of the layer files
    layersTab[0] = pd.Series(layer_files)

    #third column is count of non-Na's
    layersTab[1] = attributeDF[layer_files.keys()].count()

    #forth column is the count of 1's if the layer is binary, Na if not
    layersTab[2] = np.repeat(np.NAN,len(layers.keys()))

    layersTab.loc[datatypes['bin'],2] = attributeDF[datatypes['bin']].sum(axis=0)

    for ind in range(nlayouts):
        layersTab[3+ind] = np.repeat(np.nan, layersTab.shape[0])

    layersTab.to_csv(directory + '/layers.tab',sep='\t',header=None)


def writeLayersTab(
        attributeDF,
        layers,
        layer_files,
        densityArray,
        datatypes,
        options):
    '''
    :param attributeDF: the pandas data frame holding attribute values
    :param densityArray: an array of series, each of which are returned by
                         densityOpt()
    :param layer_files: layer_files are the names of each layer
                        produced when they are written one by one to the given
                        directory
    :return: Layers.tab is a file used to build the UI,
             the format is tab delimited: layout_name, layout_file, number we
             have data for, (if binary how many 1's, else NA)
             and then each density
    '''

    #have a dict of attribute names pointing to their layer_x.tab file
    layer_files = trimLayerFiles(layer_files)
    #making an empty data frame and then filling each one of the columns
    layersTab = pd.DataFrame(index=layer_files.keys())

    #second column is the name of the layer files
    layersTab[0] = pd.Series(layer_files)

    #third column is count of non-Na's
    layersTab[1] = attributeDF[layer_files.keys()].count()

    #forth column is the count of 1's if the layer is binary, Na if not
    layersTab[2] = np.repeat(np.NAN,len(layers.keys()))

    layersTab.loc[datatypes['bin'],2] = attributeDF[datatypes['bin']].sum(axis=0)

    #the rest of the columns are the density for each layout (in order)
    for it, series_ in enumerate(densityArray):
        #fill all density with NAN in case we don't have some in the density array
        layersTab[3+it] = np.repeat(np.NAN,len(layers.keys()))
        #put the density in the dataframe
        layersTab[3+it] = series_.apply(sigDigs)

    layersTab.to_csv(options.directory + '/layers.tab',sep='\t',header=None)


def writeToDirectoryLee(
        dirName,
        leeMatrix,
        simMatrix,
        colNameList,
        layers,
        index=0):
    '''
    this function writes the computed similarities, i.e. lees L, to a directory
    if we wanted to do p-values or something else computations for corrections
    would be done here

    The way this works is that the sign of the correlation informs the
    positive-negative selection
    and they are ranked by closness to zero of the pvalue
    :param dirName: ends in '/'
    :param colNameList: needs to be in the same order as the leeMatrix names
    :param layers is a dataframe, read in from layers.tab
    :return: writes files in the proper format to the directory dirName

    dirName = '/home/duncan/trash/statsL'
    '''

    assert(dirName[-1] == '/')
    for i,column in enumerate(colNameList):
        #print getLayerIndex(column,layers)
        statsO = pd.DataFrame(index= colNameList)
        statsO[0] = leeMatrix[i,]
        #truncate as an attempt to be reproducible on different machines.
        statsO[0] = truncateNP(statsO[0],11)

        #place holder for rank, need because of use of parallel structures
        # simMat and leeMat
        statsO[1] = np.repeat(np.NAN,statsO.shape[0])

        statsO[2] = simMatrix[i,]

        statsO = statsO.iloc[statsO.index!=column] #get rid of identity

        # second column is how the UI ranks, it uses that column and the sign
        # of leesL
        # to determine order
        statsO[1] = 1- (stats.rankdata(np.abs(statsO[0]),method='average') / (statsO.shape[0]))

        filename = 'statsL_'+ getLayerIndex(column,layers)+ '_' + str(index) + '.tab'

        statsO = statsO.apply(lambda x: x.apply(sigDigs))
        statsO.to_csv(dirName+filename,sep='\t',header=None)


def writeToFileLee(fout, leeLV, simV, colNames):
    '''
    write a single lees L to file, for use with singleLeesL function
    @param fout:
    @param leeLV:
    @param simV:
    @param colNames:
    @return:
    '''
    #truncate as an attempt to be reproducible on different machines.
    # also needed to properly determine ranks are equal when vectors have
    #  -1 correlation
    # ( so the leeL values are -.xxxxxxxxx3 and .xxxxxxxxx4, and should have
    # been determined
    # .xxxxxxxxx35 and .xxxxxxxxx35 )
    leeLV = truncateNP(leeLV, 11)
    #ranks is how the UI knows the order in which to display
    ranks =  1- (stats.rankdata(np.abs(leeLV),method='average') / len(leeLV))
    outDF = pd.DataFrame({0:leeLV,1:ranks,2:simV},index=colNames)
    #apply significant digit cutoff of 7 to all the numbers in table
    outDF = outDF.apply(lambda x: x.apply(sigDigs))

    outDF.to_csv(fout,sep='\t',header=None)


def trimLayerFiles(layer_files):
    '''
    :param layer_files: dict { layer_name -> layer path, ... , ... }
    :return: a similar dict with the layer paths trimmed to only by the file name
    this is needed for writing out the layers.tab file...
    '''
    for attr in layer_files.keys():
        layer_files[attr] = layer_files[attr].split('/')[-1]
    return layer_files


def getLayerIndex(layerName, layers):
    filename = layers[1].loc[layerName]
    return filename[filename.index('_')+1:filename.index('.')]
