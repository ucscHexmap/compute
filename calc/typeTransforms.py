"""
Collection of type transforms.
"""
import pandas as pd


def dictToPandasSeries(focusAttr):
    """
    :param focusAttr: { "attrName" : {"nodeId": nodeValue, ... } }
    :return: pandas series
    """
    attrName = focusAttr.keys()[0]
    pandasSeries = pd.DataFrame(focusAttr)[attrName]
    return pandasSeries


def numpyToPandas(mat, col_list, row_list):
    return pd.DataFrame(mat, index=row_list, columns=col_list)


def pandasToNumpy(df):
    '''
    does conversion of a pandas data frame to type returned by read_tabular
    @param df: pandas data frame
    @return: numpy.array, column list, row list
    '''

    mat = df.as_matrix()
    col_list = df.columns.values.tolist()
    row_list = df.index.tolist()

    return mat, col_list, row_list
