#!/usr/bin/env python2.7

# This tests the dataset database functionality.

import os
from datetime import date
import json

import unittest
import testUtil as util
from cellDatasetDb import CellDatasetDb
import cellDataset as dataset


testDir = os.path.join(os.environ.get('HEXCALC'), 'www/cellDb/tests')
dbPath = os.path.join(testDir, 'out/datasetDb.db')

isoToday = date.today().isoformat()

data = [
    ['Immune Bone', 'immune bone', 'human', 378000],
    ['Hemotopoietic', 'blood', 'human', 681],
    ['Tabula Muris droplet',
     'Bladder, Heart_and_Aorta, Kidney, Limb_Muscle, Liver, Lung, Mammary_Gland, Marrow, Spleen, Thymus, Tongue, Trachea',
     'mouse: Tabula Muris', 70118],
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
        dataset.addMany(data, dbPath)
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
            os.path.join(testDir, 'in/datasetAddFromFile.tsv'), dbPath)
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
            os.path.join(testDir, 'in/datasetAddFromFile.tsv'), dbPath, True)
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
        r = s.db.addOne('Hemotopoietic', 'blood', 'human', 681)

        # Verify correct ID was returned.
        # print 'r:', r
        s.assertEqual(1, r);

        # Verify fields were initialized properly.
        out = s.db.getOne(1)
        #print 'out:', out
        s.assertEqual(1, out[s.db.idI])
        s.assertEqual('Hemotopoietic', out[s.db.nameI])
        s.assertEqual('blood', out[s.db.organI])
        s.assertEqual('human', out[s.db.speciesI])
        s.assertEqual(681, out[s.db.sampleCountI])

    def test_deleteAll_db(s):
        s.db.addMany(data)
        s.db.deleteAll()
        r = s.db.hasData()
        # print 'test_getAll:r:', r
        s.assertEqual(False, r)


    def test_deleteAll_api(s):
        s.db.addMany(data)
        dataset.deleteAll(dbPath)
        r = s.db.hasData()
        s.assertEqual(False, r)


    def test_hasData_db(s):
        r = s.db.addOne('Hemotopoietic', 'blood', 'human', 681)
        hasData = s.db.hasData()
        s.assertEqual(True, hasData)


    def test_getAll_api(s):
        s.db.addMany(data)
        r = dataset.getAll(dbPath)
        #print 'test_getAll:r:', r
        for i, row in enumerate(r['datasetInfo']):
            for j, col in enumerate(row):
                if j == 0:
                    s.assertEqual(i+1, col)
                else:
                    s.assertEqual(data[i][j-1], col)


    if __name__ == '__main__':
        unittest.main()
