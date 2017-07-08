#!/usr/bin/env python2.7
"""
utils.py
Misc. utilities for the server python code
"""
import os, math, traceback
import numpy as np
import pandas as pd

#The following functions are for shared by modules and used to read in data
def readXYs(fpath):
    '''
    reads the xy positions from file
    :param fpath: file path  to tab seperated x-y position file, 1st col should
                  be row names
    :return: a pandas data frame with index set to node Ids and the
    '''

    return pd.read_csv(fpath,sep='\t',index_col=0,comment='#',header=None)


def readPandas(datafile):
    """
    This reads data into a pandas dataframe following these specifications.
    >the file is tab separated
    >ignore lines with '#'
    >if the first line not hidden with '#' is all strings, then it is a header
    >the first column holds the row names
    @param datafile:
    @return: pandas DataFrame
    """

    header_line = _headerLine(datafile)
    comment_char = '#'

    df = pd.read_table(datafile,
                       index_col=0,
                       comment=comment_char,
                       header=header_line
                       )
    # Put the filename as the index name
    df.index.name = datafile
    return df

def _headerLine(datafile):
    read_header = _firstLineHasAllStrs(datafile)
    if read_header:
        read_header = 0
    else:
        read_header = None
    return read_header

def _firstLineHasAllStrs(datafile):
    return _hasAllStrs(_firstLineArray(datafile))

def _firstLineArray(datafile):
    with open(datafile) as fin:
        for line in fin:
            line = line.strip()
            if line[0] != "#":
                return line.split("\t")

def _hasAllStrs(line_array):
    all_strs = len(line_array)
    n_strs = np.sum([_isStr(thing) for thing in line_array])
    return n_strs == all_strs

def _isStr(thing):
    t = type(thing)
    return t == str or t == unicode

def getAttributes(fileNameList,dir='',debug=False):
    '''
    creates a single attribute/metadata dataframe (pandas) from a list of filenames
     expects rows to be similar (describing nodes in tumor map format) and
     columns to describe each attribute or unit of metadata

    NOte: adds a '/' to the end of dir if not there

    :param fileNameList: this is a list of attribute matrices
    :param dir: this is the name of the directory that attributes are in
    :return: a pandas dataframe with all the attributes for a given map
    '''
    if debug:
        print 'getAttributes() called with'
        print fileNameList

    # TODO: the standard way to handle this is always use os.path.join() to
    # join any sort of paths.
    if (len(dir) > 0 and dir[-1]!= '/'):
        dir+='/'

    dfs = [] #list to hold individual dfs
    for filename in fileNameList:
        #try except allows filname to be a str buffer
        try:
            filename = dir + filename
        except TypeError:
            pass

        #assume first column is row name and do below to get rid of duplicates
        df = pd.read_csv(filename,sep='\t',dtype='str')#,index_col=0)

        if debug:
            print "column names for attr file: " + str(df.columns)

        dfs.append(df.drop_duplicates(subset=df.columns[0], keep='last').set_index(df.columns[0]))

    #stich all attributes together
    allAtts = pd.concat(dfs,axis=1)

    #turn what attributes that don't throw an error into a float
    for colname in allAtts.columns:
        try:
            allAtts[colname] = allAtts[colname].astype(np.float)
        except ValueError as e:
            pass

    return allAtts

def sigDigs(x, sig=7,debug=False):

    if sig < 1:
        raise ValueError("number of significant digits must be >= 1")
        return

    if debug:
        print x, type(x)

    if math.isnan(x):
        return float('NaN')

    # Use %e format to get the n most significant digits, as a string.
    format = "%." + str(sig-1) + "e"
    
    # Then convert back to a float
    return float(format % x)

def toFloat(x):
    try:
        return float(x)
    except ValueError:
        return float('NaN')

def truncate(f, n):
    '''
    Truncates/pads a float f to n decimal places without rounding
    taken from http://stackoverflow.com/questions/783897/truncating-floats-in-python
    @param f: the floating point number to be truncated
    @param n: the number of decimal places we wish to keep
    @return: a float f to n decimal places without rounding
    '''
    if np.isnan(f):
        return np.NAN

    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])

#this makes the function truncate easily/efficiently applyable to every cell in an  numpy array
#http://stackoverflow.com/questions/7701429/efficient-evaluation-of-a-function-at-every-cell-of-a-numpy-array
truncateNP = np.vectorize(truncate,otypes=[np.float])
