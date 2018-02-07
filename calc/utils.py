#!/usr/bin/env python2.7
"""
utils.py
Misc. utilities for the server python code
"""
import os, math, traceback
import numpy as np
import pandas as pd
import formatCheck

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

    headerLineNumber = _headerLine(datafile)
    comment_char = '#'

    # If we found a header, check for duplicates.
    if headerLineNumber is not None:
        duplicates_check(_firstLineArray(datafile))

    df = pd.read_csv(datafile,
                       index_col=0,
                       comment=comment_char,
                       header=headerLineNumber,
                       sep="\t",
                       )

    # Put the filename as the index name
    df.index.name = datafile
    return df


def duplicates_check(list_):
    s = pd.Series(list_)
    dups = s[s.duplicated()]
    n_dups = len(dups)
    if n_dups:
        if n_dups > 100:
            message = "Over 100 duplicate ids found. " \
                      "Identifiers need to be unique for proper processing"
        else:
            message = "Duplicate ids found. " \
                      "Identifiers need to be unique for proper processing." \
                      "They are: \n" + "\n".join(dups)

        raise ValueError(message)


def duplicate_columns_check(df):
    """
    Throw a value error if duplicate columns are found.
    @param df: pandas dataframe
    @return: None
    """
    duplicates_check(df.columns)


def nCols(filename):
    """
    Count number of columns in a tab separated file.
    @param filename:
    @return: int, number of columns in the file
    """
    n_cols = -1
    with open(filename, "r") as fin:
        for line in fin:
            if line.strip()[0] != "#":
                n_cols = len(line.split("\t"))
                break

    return n_cols


def _headerLine(datafile):
    """
    Determines whether or not there is a header.
    Logic is, if it is a 3 line file either the header is as specified in
    formatCheck.py, or there is no header.
    @param datafile:
    @return:
    """
    # Usually header line will be the first line.
    header_line = 0
    # If the file has three columns there may or may not be a header.
    n_cols = nCols(datafile)
    if n_cols == 3:
        if formatCheck.type_of_3col(datafile) == "NOT_VALID":
            header_line = None

    return header_line


def _firstLineArray(filename):
    with open(filename,'r') as fin:
        # Only reads the first line.
        for line in fin:
            return line.strip().split("\t")


def tabFilesToDF(fileNameList, dir=''):
    '''
    Creates a single attribute/metadata dataframe (pandas) from a list
    of tab delimeted files.
    Rows in each file should overlap with other files in the list.
    Columns describe an attribute or unit of metadata.
    All columns are converted to float unless an error is thrown.

    :param fileNameList: this is a list of attribute matrices
    :param dir: this is the name of the directory that attributes are in
    :return: a pandas dataframe with all the attributes for a given map
    '''

    dfs = []
    for filename in fileNameList:
        # Allow the filename to be a stringIO buffer.
        try:
            filename = os.path.join(dir, filename)
        except AttributeError:
            pass

        df = pd.read_csv(filename, sep='\t', dtype='str')

        df = df.drop_duplicates(subset=df.columns[0], keep='last')
        df = df.set_index(df.columns[0])
        dfs.append(df)

    # Make one dataframe out of the many.
    allAtts = pd.concat(dfs, axis=1)

    # Float conversion.
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

# Make the truncate function able to apply to an numpy array.
truncateNP = np.vectorize(truncate,otypes=[np.float])
