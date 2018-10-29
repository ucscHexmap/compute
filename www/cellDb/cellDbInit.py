
#

import os
from cellDbCluster import CellDbCluster
from cellDbClusterAttr import CellDbClusterAttr
from cellDbDataset import CellDbDataset
from cellDbSampleAttr import CellDbSampleAttr
from cellDbTrajectory import CellDbTrajectory

dbFileName = 'cell.db'

# Table objects
cluster = None
clusterAttr = None
dataset = None
sampleAttr = None
trajectory = None


def Cluster ():
    return cluster


def ClusterAttr ():
    return clusterAttr


def Dataset ():
    return dataset


def SampleAttr ():
    return sampleAttr


def Trajectory ():
    return trajectory


def init(appCtx):
    dbPath = os.path.join(appCtx.databasePath, dbFileName)

    global cluster
    cluster = CellDbCluster(dbPath)
    global clusterAttr
    clusterAttr = CellDbClusterAttr(dbPath)
    global dataset
    dataset = CellDbDataset(dbPath)
    global sampleAttr
    sampleAttr = CellDbSampleAttr(dbPath)
    global trajectory
    trajectory = CellDbTrajectory(dbPath)
