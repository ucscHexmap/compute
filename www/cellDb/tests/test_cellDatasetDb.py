#!/usr/bin/env python2.7

# This tests the dataset database functionality.

import os
from datetime import date
import json

import unittest
import testUtil as util
from util_web import Context
from cellDatasetDb import CellDatasetDb
import cellDataset as dataset


testDir = os.path.join(os.environ.get('HEXCALC'), 'www/cellDb/tests')
appCtxDict = {
    'databasePath': os.path.join(testDir, 'out'),
}
appCtx = Context(appCtxDict)
dbPath = os.path.join(appCtx.databasePath, 'datasetDb.db')

isoToday = date.today().isoformat()

data = [
    ['Immune Bone', 'immune bone', 'human', 378000, 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd'],
    ['Hemotopoietic', 'blood', 'human', 681, 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd'],
    ['Tabula Muris droplet',
     'Bladder, Heart_and_Aorta, Kidney, Limb_Muscle, Liver, Lung, Mammary_Gland, Marrow, Spleen, Thymus, Tongue, Trachea',
     'mouse: Tabula Muris', 70118, 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd'],
]


class Test_cellDatasetDb(unittest.TestCase):


    def setUp(self):
        try:
            os.remove(dbPath)
        except:
            pass
        self.db = CellDatasetDb(dbPath)


    def test_addMany_db(s):
        s.db.addMany(data)
        r = s.db.getAll()
        # print 'test_addMany:r:', r
        for i, row in enumerate(r):
            for j, col in enumerate(row):
                if j == 0:
                    s.assertEqual(i + 1, col)
                else:
                    s.assertEqual(data[i][j - 1], col)


    def test_addMany_api(s):
        dataset.addMany(data, appCtx)
        r = s.db.getAll()
        # print 'r:', r
        for i, row in enumerate(r):
            for j, col in enumerate(row):
                if j == 0:
                    s.assertEqual(i + 1, col)
                else:
                    s.assertEqual(data[i][j - 1], col)


    def test_addManyFromFile_db(s):
        s.db.addManyFromFile(os.path.join(testDir, 'in/datasetAddFromFile.tsv'))
        r = s.db.getAll()
        # print 'test_addMany:r:', r
        for i, row in enumerate(r):
            for j, col in enumerate(row):
                if j == 0:
                    s.assertEqual(i + 1, col)
                else:
                    s.assertEqual(data[i][j - 1], col)


    def test_addManyFromFile_api(s):
        s.db.addMany(data)
        dataset.addManyFromFile(
            os.path.join(testDir, 'in/datasetAddFromFile.tsv'), appCtx)
        r = s.db.getAll()
        # print 'r:', r
        s.assertEqual(6, len(r))
        for i, row in enumerate(r[3:]):
            for j, col in enumerate(row):
                if j == 0:
                    s.assertEqual(i + 4, col)
                else:
                    s.assertEqual(data[i][j - 1], col)


    def test_addManyFromFileReplace_api(s):
        s.db.addMany(data)
        dataset.addManyFromFile(
            os.path.join(testDir, 'in/datasetAddFromFile.tsv'), appCtx, True)
        r = s.db.getAll()
        #print 'r:', r
        s.assertEqual(3, len(r))
        for i, row in enumerate(r):
            for j, col in enumerate(row):
                if j == 0:
                    s.assertEqual(i + 4, col)
                else:
                    s.assertEqual(data[i][j - 1], col)


    def test_addOne_db(s):
        r = s.db.addOne(data[1])

        # Verify correct ID was returned.
        # print 'r:', r
        s.assertEqual(1, r);

        # Verify fields were initialized properly.
        out = s.db.getOne(1)
        #print 'out:', out
        s.assertEqual(1, out[0])
        s.assertEqual('Hemotopoietic', out[1])
        s.assertEqual('blood', out[2])
        s.assertEqual('human', out[3])
        s.assertEqual(681, out[4])


    def test_deleteAll_db(s):
        s.db.addMany(data)
        s.db.deleteAll()
        r = s.db.hasData()
        # print 'test_getAll:r:', r
        s.assertEqual(False, r)


    def test_deleteAll_api(s):
        s.db.addMany(data)
        dataset.deleteAll(appCtx)
        r = s.db.hasData()
        s.assertEqual(False, r)


    def test_hasData_db(s):
        r = s.db.addOne(data[0])
        hasData = s.db.hasData()
        s.assertEqual(True, hasData)


    def test_getAll_api(s):
        s.db.addMany(data)
        r = dataset.getAll(appCtx)
        #print 'test_getAll:r:', r
        for i, row in enumerate(r):
            for j, col in enumerate(row):
                if j == 0:
                    s.assertEqual(i+1, col)
                else:
                    s.assertEqual(data[i][j-1], col)


    if __name__ == '__main__':
        unittest.main()
