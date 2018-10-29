#!/usr/bin/env python2.7

# This tests the cell database administrative functionality.

import os

import unittest
from util_web import Context
import cellDbInit
import cellDbAdmin as admin

testDir = os.path.join(os.environ.get('HEXCALC'), 'www/cellDb/tests')
appCtxDict = {
    'databasePath': os.path.join(testDir, 'out'),
    'unitTest': True,
}
appCtx = Context(appCtxDict)
dbPath = os.path.join(appCtx.databasePath, 'cell.db')

clusterFileName = 'in/clusterAddFromFile.tsv'
clusterData = [
    ['cname1', 7, 10],
    ['cname2', 8, 11],
    ['cname3', 9, 12],
]

clusterAttrFileName = 'in/clusterAttrAddFromFile.tsv'
clusterAttrData = [
    ['caname1', 'val1', 16],
    ['caname2', 'val2', 17],
    ['caname3', 'val3', 18],
]

datasetFileName = 'in/datasetAddFromFile.tsv'
datasetData = [
    ['Immune Bone', 'immune bone', 'human', 378000, 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd'],
    ['Hemotopoietic', 'blood', 'human', 681, 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd'],
    ['Tabula Muris droplet',
     'Bladder, Heart_and_Aorta, Kidney, Limb_Muscle, Liver, Lung, Mammary_Gland, Marrow, Spleen, Thymus, Tongue, Trachea',
     'mouse: Tabula Muris', 70118, 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd'],
]

sampleAttrFileName = 'in/sampleAttrAddFromFile.tsv'
sampleAttrData = [
    ['sname1', 13],
    ['sname2', 14],
    ['sname3', 15],
]

trajectoryFileName = 'in/trajectoryAddFromFile.tsv'
trajectoryData = [
    ['name1', 1, 4],
    ['name2', 2, 5],
    ['name3', 3, 6],
]

def test__add(s, table, data, fileName):
    table.addMany(data)
    admin.add(os.path.join(testDir, fileName),
              table, appCtx)
    r = table.getAll()
    # print 'r:', r
    s.assertEqual(6, len(r))
    for i, row in enumerate(r[3:]):
        for j, col in enumerate(row):
            if j == 0:
                s.assertEqual(i + 4, col)
            else:
                s.assertEqual(data[i][j - 1], col)


def test__add_replace(s, table, data, fileName):
    table.addMany(data)
    admin.add(os.path.join(testDir, fileName),
              table, appCtx, True)
    r = table.getAll()
    # print 'r:', r
    s.assertEqual(3, len(r))
    for i, row in enumerate(r[3:]):
        for j, col in enumerate(row):
            if j == 0:
                s.assertEqual(i + 4, col)
            else:
                s.assertEqual(data[i][j - 1], col)


def test__getAll(s, table, data):
    table.addMany(data)
    r = admin.getAll(table, appCtx)
    # print 'r:', r
    s.assertEqual(3, len(r))
    for i, row in enumerate(r):
        for j, col in enumerate(row):
            if j == 0:
                s.assertEqual(i + 1, col)
            else:
                s.assertEqual(data[i][j - 1], col)


class Test_cellDbAdmin(unittest.TestCase):


    def setUp(s):
        try:
            os.remove(dbPath)
        except:
            pass
        cellDbInit.init(appCtx)
        s.clusterAttr = cellDbInit.ClusterAttr()
        s.cluster = cellDbInit.Cluster()
        s.dataset = cellDbInit.Dataset()
        s.sampleAttr = cellDbInit.SampleAttr()
        s.trajectory = cellDbInit.Trajectory()


    def test_addClusters(s):
        test__add(s, s.cluster, clusterData, clusterFileName)


    def test_getAllClusters(s):
        test__getAll(s, s.cluster, clusterData)



    def test_addClusterAttrs(s):
        test__add(s, s.clusterAttr, clusterAttrData, clusterAttrFileName)


    def test_getAllClusterAttrs(s):
        test__getAll(s, s.clusterAttr, clusterAttrData)



    def test_addDatasets(s):
        test__add(s, s.dataset, datasetData, datasetFileName)


    def test_addDatasets_replace(s):
        test__add_replace(s, s.dataset, datasetData, datasetFileName)


    def test_getAllDatasets(s):
        test__getAll(s, s.dataset, datasetData)



    def test_addSampleAttrs(s):
        test__add(s, s.sampleAttr, sampleAttrData, sampleAttrFileName)


    def test_getAllSampleAttrs(s):
        test__getAll(s, s.sampleAttr, sampleAttrData)



    def test_addTrajectories(s):
        test__add(s, s.trajectory, trajectoryData, trajectoryFileName)


    def test_getAllTrajectories(s):
        test__getAll(s, s.trajectory, trajectoryData)


    if __name__ == '__main__':
        unittest.main()
