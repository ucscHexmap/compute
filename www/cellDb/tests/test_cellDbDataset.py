#!/usr/bin/env python2.7

# This tests the dataset database functionality.

import os
import unittest
from util_web import Context
import cellDbInit
import cellDbDataset


testDir = os.path.join(os.environ.get('HEXCALC'), 'www/cellDb/tests')
appCtxDict = {
    'databasePath': os.path.join(testDir, 'out'),
}
appCtx = Context(appCtxDict)
dbPath = os.path.join(appCtx.databasePath, 'cell.db')

data = [
    ['Immune Bone', 'immune bone', 'human', 378000, 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd'],
    ['Hemotopoietic', 'blood', 'human', 681, 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd'],
    ['Tabula Muris droplet',
     'Bladder, Heart_and_Aorta, Kidney, Limb_Muscle, Liver, Lung, Mammary_Gland, Marrow, Spleen, Thymus, Tongue, Trachea',
     'mouse: Tabula Muris', 70118, 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd'],
]


class Test_cellDbDataset(unittest.TestCase):


    def setUp(self):
        try:
            os.remove(dbPath)
        except:
            pass
        cellDbInit.init(appCtx)
        self.db = cellDbInit.Dataset()


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


    def test_addManyFromFileReplace_db(s):
        s.db.addMany(data)
        s.db.addManyFromFile(
            os.path.join(testDir, 'in/datasetAddFromFile.tsv'), True)
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


    def test_hasData_db(s):
        r = s.db.addOne(data[0])
        hasData = s.db.hasData()
        s.assertEqual(True, hasData)


    if __name__ == '__main__':
        unittest.main()
