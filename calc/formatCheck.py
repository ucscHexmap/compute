"""
This module provides a warning function, which should be used to determine if
the layoutInputFile matches the users layoutInputFormat specification.
"""

import numpy as np
import utils

def warnAboutFormat(df,expected_type):
    """
    This function produces a string detailing the difference between the
    inferred type of the layoutInputFormat and the expected type (expected
    type being the one entered from the command line). If there is no
    difference the function returns a boolean False value.
    @param df: The layoutInputFile read into a pandas dataframe with the first
    column being the rows names
    @param expected_type: The layoutInputFormat comming from the command line.
    @return: (bool) False, or (str) warning message.
    """
    inferred_type = _layoutInputFormat(df)
    message = False
    if expected_type != inferred_type:
        if expected_type == 'sparseSimilarity':
            message = """The layoutInputFormat chosen was 'sparseSimilarity',
                         but the inferred type was '""" + inferred_type + """'
                         . The layoutInputFile was not recognized as a
                         3 column matrix with string identifiers in the first
                         and second columns."""

        if expected_type == 'fullSimilarity':
            message = """The layoutInputFormat chosen was 'fullSimilarity',
                         but the inferred type was '""" + inferred_type + """'
                         . The layoutInputFile was not recognized as being
                         symmetric."""

        if expected_type == 'xyPositions':
            message = """The layoutInputFormat chosen was 'xyPositions',
                         but the inferred type was '""" + inferred_type + """'
                         . The layoutInputFile was not recognized as having 2
                         columns with integers or floats that has NO missing
                         data."""

        if expected_type == 'clusterData':
            message = """The layoutInputFormat chosen was 'clusterData',
                         but the inferred type was '""" + inferred_type + """'
                         . The layoutInputFile was not recognized as a
                         matrix of arbitrary shape with no string or boolean
                         values."""

        else:
            message = """The layoutInputFormat chosen was not recognized by
                         the formatCheck module. The inferred type was: """ \
                         + inferred_type
    return message


def _layoutInputFormat(df):
    """Produce a string that is either a valid layout input format or unknown"""


    format_ = 'unknown'
    # Three columns can mean xy or sparse.
    if df.shape[1] == 2:
        if _isSparseSimilarity(df):
            format_ = 'sparseSimilarity'

        elif _isXYPositions(df):
            format_ = 'xyPositions'
            # This catches the edge case where nodeIds are either floats or
            # ints, in that case we can not determine whether this file
            # is a sparse or an xy positions file.
            if df.index.dtype == 'float64' or df.index.dtype == 'int64':
                raise ValueError("Cannot not determine input format type: "
                                 "distinguish by putting a proper header in the "
                                 "input file, 'node node edge' for sparse "
                                 "similarity or 'node x y' for an xy positions "
                                 "file")
    else:
        if _isFullSimilarity(df):
            format_ = 'fullSimilarity'

        elif _isClusterData(df):
            format_ = 'clusterData'



    return format_


def _isFullSimilarity(df):
    """Uses symetric property to determine whether the input is full
    similarity"""

    passed = False
    if df.shape[1] == df.shape[0]:
        passed = np.allclose(
            df.as_matrix().transpose(),
            df.as_matrix(),
            equal_nan=True
        )
    return passed


def _isSparseSimilarity(df):
    """Uses the shape and datatype of the first columns to determine whether
    the input is sparse similarity"""

    exp_ncols = df.shape[1] == 2
    exp_type  = (df[df.columns[0]].dtype == "object"
                or df[df.columns[0]].dtype == "str") \
                and (df[df.columns[1]].dtype == "int64"
                or df[df.columns[1]].dtype == "float64" )

    return exp_ncols and exp_type


def _isClusterData(df):
    """Uses the datatype of each column to determine whether the input is
    clustering data"""

    dtypes_ = map(str, df.dtypes.tolist())
    return "object" not in dtypes_ and "bool" not in dtypes_


def _isXYPositions(df):
    """Uses the number of columns, datatype, and the prerequisite that there
    are no missing values to determine whether the input is xy positions"""

    # Two columns are expected.
    exp_ncols = df.shape[1] == 2

    # The x and y columns should only contain numbers.
    xColNumbers = df[df.columns[0]].dtype == "float" \
                  or df[df.columns[0]].dtype == "int"
    yColNumbers = df[df.columns[1]].dtype == "float" \
                  or df[df.columns[1]].dtype == "int"
    exp_type = xColNumbers and yColNumbers

    zero_nas = not bool(df.isnull().sum().sum())
    return exp_type and exp_ncols and zero_nas


def _validHeaderOf3Col():

    return {
        "xyPositions" : ["node", "x", "y"],
        "sparseSimilarity" : ["node", "node", "edge"]
    }


def type_of_3col(header_array):
    header_array = map(lambda x: x.lower(), header_array)
    valid_header_dict = _validHeaderOf3Col()
    for header in valid_header_dict.keys():
        if header_array == valid_header_dict[header]:
            return header
    return "NOT_VALID"