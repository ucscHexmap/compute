
#

import os
from cellDbDataset import CellDbDataset
from cellDbTrajectory import CellDbTrajectory

dbFileName = 'cell.db'

# Table objects
dataset = None
trajectory = None


def Dataset ():
    return dataset


def Trajectory ():
    return trajectory


def init(appCtx):
    dbPath = os.path.join(appCtx.databasePath, dbFileName)

    global dataset
    dataset = CellDbDataset(dbPath)
    global trajectory
    trajectory = CellDbTrajectory(dbPath)
