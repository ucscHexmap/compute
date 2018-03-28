#!/usr/bin/env python

import collections as collect

def make_unique(list):
    '''
    :param list: a list of strings
    :return: a new list with IDs made unique by adding a number to each
        nonunique element and a new list containing IDs that were modified.
    '''

    countD = collect.Counter()
    uniqueList = []
    dupList = []
    for ent in list:
        if countD[ent]:
            newEnt = ent+'.' + str(countD[ent])
            uniqueList.append(newEnt)
            dupList.append(newEnt)
        else:
            uniqueList.append(ent)

        countD[ent]+=1

    return(uniqueList, dupList)
