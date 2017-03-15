#!/usr/bin/env python2.7


import os
import unittest

testDir = os.getcwd()
inDir = os.path.join(testDir, 'in/stats/')   # The input data
expDir = os.path.join(testDir, 'exp/stats/') # The expected output data
outDir = os.path.join(testDir, 'out/stats/') # The actual output data

import layout
import testUtil as util

class Test_stats(unittest.TestCase):

    def runPy(s):
    
        # Build the parms to be passed to layout.py
        opts = [
            '--similarity', inDir + 'artificial_sparse.tab',
            '--names', 'mRNA',
            '--scores', inDir + 'attributes.tabstringed',
            '--colormaps', inDir + 'colormaps.tab',
            '--first_attribute', 'Subtype',
            '--directory', outDir,
        ]
        
        #clear output directory
        util.removeOldOutFiles(outDir)
        
        # Run the layout
        layout.main(opts)

    def test_stats(s):
        s.runPy()
        util.compareActualVsExpectedDir(s, outDir, expDir)


if __name__ == '__main__':
    unittest.main()
