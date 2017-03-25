#!/usr/bin/env python2.7


import sys
import unittest
from rootDir import getRootDir

outDirBase = '/hive/groups/hexmap/dev/view/swat_soe.ucsc.edu/'
#outDirBase = '/Users/swat/data/view/swat_soe.ucsc.edu/'

# NOTE: until we get selenium up, this is how we test the UI
"""
First create maps from the UI using the map names and input data below and the 
appropriate feature data type.
Then run this script to compare the output with the expected.

    MAP NAME       INPUT DATA in in/layout/
    raw_no_atts    full_matrix.tab
    raw_no_colors  full_matrix.tab, attributes.tab
    full_no_atts   mcr.fullsim.stable.tab
    top6_no_atts   mcr.top6.stable.tab
    xy_no_atts     exp/layoutBasic/xyPreSquiggle_0.tab
"""

rootDir = getRootDir()

# These dirs should depend only on the above rootDir
# using the repository directory structure starting at 'hexagram/'
testDir = rootDir + 'tests/pyUnittest/'
inDir = testDir + 'statsIn/'   # The input data
expXyDir = testDir + 'exp/layoutBasicXy/'

import testUtil as util

class Test_createMapUi(unittest.TestCase):

    def test_raw_no_atts(s):
    
        outDir = outDirBase + 'raw_no_atts'
        expDir = testDir + 'exp/layoutBasicNoAtts/'
        util.compareActualVsExpectedDir(s, expDir, outDir)

    def test_raw_no_colors(s):
    
        outDir = outDirBase + 'raw_no_colors'
        expDir = testDir + 'exp/layoutBasicNoColor/'
        util.compareActualVsExpectedDir(s, expDir, outDir)

    def test_full_no_atts(s):
    
        outDir = outDirBase + 'full_no_atts'
        expDir = testDir + 'exp/layoutBasicNoAtts/'
        util.compareActualVsExpectedDir(s, expDir, outDir)

    def test_top6_no_atts(s):
    
        outDir = outDirBase + 'top6_no_atts'
        expDir = testDir + 'exp/layoutBasicNoAtts/'
        util.compareActualVsExpectedDir(s, expDir, outDir)

    def test_xy_no_atts(s):
    
        outDir = outDirBase + 'xy_no_atts'
        expDir = testDir + 'exp/layoutBasicNoAtts/'
        
        #check that it is mostly the same as the other files
        util.compareActualVsExpectedDir(s, expDir, outDir,
                                        excludeFiles = ['log',
                                                        'neighbors_0.tab',
                                                        'assignments0.tab',
                                                        'hexNames.tab',
                                                        'xyPreSquiggle_0.tab']
                                        )
        # These files for xy coords are not expected to be the same as other
        # runs, but to make sure they are correct we have but previous runs in a
        # different expected directory.
        util.compareActualVsExpectedFile(s,'/neighbors_0.tab',expXyDir,outDir)
        util.compareActualVsExpectedFile(s,'/assignments0.tab',expXyDir,outDir)
        util.compareActualVsExpectedFile(s,'/xyPreSquiggle_0.tab',expXyDir,outDir)

if __name__ == '__main__':
    unittest.main()
