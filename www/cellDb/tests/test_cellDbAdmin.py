#!/usr/bin/env python2.7

# This tests the cell database administrative functionality.

import os

import unittest
from util_web import Context
import cellDbDataset as table
import cellDbAdmin as admin


testDir = os.path.join(os.environ.get('HEXCALC'), 'www/cellDb/tests')
appCtxDict = {
    'databasePath': os.path.join(testDir, 'out'),
    'unitTest': True,
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


class Test_cellDbAdmin(unittest.TestCase):


    def setUpDatasets(self):
        try:
            os.remove(dbPath)
        except:
            pass
        self.db = table.CellDbDataset(dbPath)


    def test_addDatasets(s):
        s.setUpDatasets()
        s.db.addMany(data)
        admin.addDatasets(
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


    def test_addDatasets_replace(s):
        s.setUpDatasets()
        s.db.addMany(data)
        admin.addDatasets(
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


    def test_getAllDatasets(s):
        s.setUpDatasets()
        s.db.addMany(data)
        r = admin.getAllDatasets(appCtx)
        #print 'r:', r
        s.assertEqual(3, len(r))
        for i, row in enumerate(r):
            for j, col in enumerate(row):
                if j == 0:
                    s.assertEqual(i + 1, col)
                else:
                    s.assertEqual(data[i][j - 1], col)


    if __name__ == '__main__':
        unittest.main()
