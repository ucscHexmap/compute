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