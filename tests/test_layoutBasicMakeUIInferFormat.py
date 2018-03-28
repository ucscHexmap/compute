#!/usr/bin/env python2.7

"""
TODO:
- fix test names
"""

import os
import unittest
import testUtil as util

testDir = os.getcwd()
inDir = os.path.join(testDir , 'in/layout/')   # The input data
outDirBase = os.path.join(testDir ,'out/layoutBasic')
expDirBase = os.path.join(testDir,'exp/layoutBasic')
expDir = expDirBase + '/'
#append to string base
expNoAttsDir = expDirBase+ 'NoAtts/'
expNoColorDir = expDirBase + 'NoColor/'
expXyDir = expDirBase + 'Xy/'

rawDataFile = os.path.join(inDir, 'full_matrix.tab')
fullSimDataFile = os.path.join(inDir, 'similarity_full.tab')
top6SimDataFile = os.path.join(inDir, 'similarity.tab')
coordDataFile = os.path.join(inDir,'coordinates.tab')

colorDataFile = os.path.join(inDir, 'colormaps.tab')
attsStringsFile = os.path.join(inDir ,'attributes.tab')
#now we never give layout coded attrs
attsCodedFile = os.path.join(inDir, 'attributes.tab')

import layout
from argparse import Namespace

class Test_layoutBasicMakeUIInferFormat(unittest.TestCase):

    def test_fullfromMakeUIfiles(s):
        outDir = outDirBase + '_full/'

        #options for different layout.py executions
        opts = Namespace(
            layoutInputFile = [fullSimDataFile],
            names = ["layout"],
            scores = [attsCodedFile],
            colormaps = colorDataFile,
            directory = outDir,
            singletons = True,
            clumpinessStats=False,
            mutualinfo=False,
            associations=False
        )

        util.removeOldOutFiles(outDir)
        layout.makeMapUIfiles(opts)
        util.compareActualVsExpectedDir(s, expDir, outDir)

    def test_rawfromMakeUIfiles(s):
        outDir = outDirBase + '_raw/'

        opts = Namespace(
            layoutInputFile= [rawDataFile],
            names= ["layout"],
            metric= 'spearman',
            scores= [attsCodedFile],
            colormaps= colorDataFile,
            directory= outDir,
            singletons=True,
            clumpinessStats=False,
            mutualinfo=False,
            associations=False
        )
        util.removeOldOutFiles(outDir)
        layout.makeMapUIfiles(opts)
        util.compareActualVsExpectedDir(s, expDir, outDir)

    def test_top6fromMakeUIfiles(s):
        outDir = outDirBase + '_top6/'

        opts = Namespace(
            layoutInputFile= [top6SimDataFile],
            names= ["layout"],
            scores= [attsCodedFile],
            colormaps= colorDataFile,
            directory= outDir,
            singletons=True,
            clumpinessStats=False,
            mutualinfo=False,
            associations=False
        )

        util.removeOldOutFiles(outDir)
        layout.makeMapUIfiles(opts)
        util.compareActualVsExpectedDir(s, expDir, outDir)

    def test_xy(s):
        outDir = outDirBase + '_xy/'

        opts = Namespace(
            layoutInputFile= [coordDataFile],
            names= ["layout"],
            metric= 'spearman',
            scores= [attsCodedFile],
            colormaps= colorDataFile,
            directory= outDir,
            singletons=True,
            clumpinessStats=False,
            mutualinfo=False,
            associations=False
        )

        util.removeOldOutFiles(outDir)

        layout.makeMapUIfiles(opts)
        #check that it is mostly the same as the other files
        util.compareActualVsExpectedDir(s,expDir, outDir,
                                        excludeFiles = ['log',
                                                        'mapMeta.json',
                                                        'neighbors_0.tab',
                                                        'assignments0.tab',
                                                        'hexNames.tab',
                                                        'xyPreSquiggle_0.tab']
                                        )
        util.compareActualVsExpectedFile(s,'assignments0.tab',expXyDir,outDir)
        util.compareActualVsExpectedFile(s,'xyPreSquiggle_0.tab',expXyDir,outDir)

if __name__ == '__main__':
    unittest.main()
