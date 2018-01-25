#!/usr/bin/env python

def make_unique(list):
    '''
    :param list: a list of strings
    :return: function adds a number to each nonunique element, forcing them to be unique
    '''

    countD = collect.Counter()
    uniqueList = []
    for ent in list:
        if countD[ent]:
            print(ent)
            uniqueList.append(ent+'.' + str(countD[ent]))
        else:
            uniqueList.append(ent)

        countD[ent]+=1

    return(uniqueList, dupList)
