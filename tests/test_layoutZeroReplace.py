

#!/usr/bin/env python2.7

import layout
from argparse import Namespace
import os
import numpy as np
import pandas as pd
import unittest

testDir = os.getcwd()
inDir = os.path.join(testDir , 'in/layout/')
rawDataFile = os.path.join(inDir, 'full_matrix.tab')

df = pd.read_table(rawDataFile, index_col=0)
df.iloc[3, 3] = np.nan
mat_with_na = os.path.join(testDir,"out/matrix_with_na")
df.to_csv(mat_with_na,sep='\t')

class Test_zeroReplace(unittest.TestCase):


    def test_NA_exception(s):
        """Cluster data with Na present should fail without zeroReplace
        should error.
        """

        opts = Namespace(
                layoutInputFormat = "clusterData",
                layoutInputFile = [mat_with_na],
                names = ["layout"],
                metric = 'spearman',
                directory = "out/nas",
                singletons = True,
                clumpinessStats = True,
                mutualinfo = True,
                associations = True
               )

        try:
            layout.makeMapUIfiles(opts)
            passed=False
        except ValueError:
            passed=True

        s.assertTrue(passed)

    def test_NA_fill(s):
        """Cluster data with Na present and zeroReplace
        flag should pass.
        """


        opts = Namespace(
                layoutInputFormat = "clusterData",
                layoutInputFile = [mat_with_na],
                names = ["layout"],
                metric = 'spearman',
                directory = "out/nas",
                singletons = True,
                clumpinessStats = True,
                mutualinfo = True,
                associations = True,
                zeroReplace = True
               )

        try:
            layout.makeMapUIfiles(opts)
            passed = True

        except ValueError:
            passed = False

        s.assertTrue(passed)

