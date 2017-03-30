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
expParmDir = expDirBase + 'Parm/'

rawDataFile = os.path.join(inDir, 'full_matrix.tab')
fullSimDataFile = os.path.join(inDir, 'mcr.fullsim.tab')
top6SimDataFile = os.path.join(inDir, 'similarity.tab')
coordDataFile = os.path.join(inDir,'coordinates.tab')

colorDataFile = os.path.join(inDir, 'colormaps.tab')
attsStringsFile = os.path.join(inDir ,'attributes.tab')
#now we never give layout coded attrs
attsCodedFile = os.path.join(inDir, 'attributes.tab')

import layout
import compute_sparse_matrix

class Test_layoutBasic(unittest.TestCase):

    def test_parms_renaming_deprecated_parms(s):
        outDir = outDirBase + '_parmsRenamingDeprecatedParms/'

        opts = [
            # parms renaming deprecated parms
            "--outputDirectory", outDir,
            "--firstAttribute", "mutated/not",
            "--layoutName", "layout",
            "--noLayoutIndependentStats",
            "--noLayoutAwareStats",
            "--distanceMetric", "cosine",
            "--outputTar", os.path.join(outDir, 'tar.tar'),
            "--outputZip", os.path.join(outDir, 'zip.zip'),
            "--authGroup", "myRole",
            "--colorAttributeFile", attsStringsFile,
            "--neighborCount", "9",
            
            "--feature_space", rawDataFile]

        util.removeOldOutFiles(outDir)
        layout.main(opts)
        util.compareActualVsExpectedDir(s, expParmDir, outDir,
            ['log', 'tar.tar', 'zip.zip'])

    def test_deprecated_parms_renamed(s):
        outDir = outDirBase + '_deprecatedParmsRenamed/'

        opts = [
            # parms deprecated in favor of new names
            "--directory", outDir,
            "--first_attribute", "mutated/not",
            "--names", "layout",
            "--no_layout_independent_stats",
            "--no_layout_aware_stats",
            "--metric", "cosine",
            "--output_tar", os.path.join(outDir, 'tar.tar'),
            "--output_zip", os.path.join(outDir, 'zip.zip'),
            "--role", "myRole",
            "--scores", attsStringsFile,
            "--truncation_edges", "9",
            
            "--feature_space", rawDataFile]

        util.removeOldOutFiles(outDir)
        layout.main(opts)
        util.compareActualVsExpectedDir(s, expParmDir, outDir,
            ['log', 'tar.tar', 'zip.zip'])
    
    def test_constants_replacing_deprecated_parms(s):
        outDir = outDirBase + '_constantsReplacingdeprecatedParms/'

        opts = [
            # deprecated parms replaced with constant values
            #"--directed_graph",
            #"--include-singletons",
            #"--window_size", "9999",

            # unchanged parms:
            "--feature_space", rawDataFile,
            "--names", "layout",
            "--directory", outDir,
            "--no_layout_independent_stats",
            "--no_layout_aware_stats"]

        util.removeOldOutFiles(outDir)
        layout.main(opts)
        util.compareActualVsExpectedDir(s, expNoAttsDir, outDir)
    
    def test_deprecated_parms_replaced_with_constants(s):
        outDir = outDirBase + '_deprecatedParmsReplacedWithConstants/'

        opts = [
            # deprecated parms replaced with constant values
            "--directed_graph",
            "--include-singletons",
            "--window_size", "9999",

            # unchanged parms:
            "--feature_space", rawDataFile,
            "--names", "layout",
            "--directory", outDir,
            "--no_layout_independent_stats",
            "--no_layout_aware_stats"]

        util.removeOldOutFiles(outDir)
        layout.main(opts)
        util.compareActualVsExpectedDir(s, expNoAttsDir, outDir)
    
    def test_full_no_feature_file(s):
        outDir = outDirBase + '_junk/'

        opts = [
            "--names", "layout",
            "--metric", 'spearman',
            "--directory", outDir,
            "--include-singletons",
            "--no_layout_independent_stats",
            "--no_layout_aware_stats"]

        util.removeOldOutFiles(outDir)
        try:
            rc = 0
            rc = layout.main(opts)
            s.assertTrue(rc, 'this should have failed')
        except ValueError as e:
            s.assertTrue(e, e)

    def test_full_no_atts(s):
        outDir = outDirBase + '_full_no_atts/'

        opts = [
            "--similarity_full", fullSimDataFile,
            "--names", "layout",
            "--metric", 'spearman',
            "--directory", outDir,
            "--include-singletons",
            "--no_layout_independent_stats",
            "--no_layout_aware_stats"]

        util.removeOldOutFiles(outDir)
        layout.main(opts)
        util.compareActualVsExpectedDir(s, expNoAttsDir, outDir)

    def test_full_no_color(s):
        outDir = outDirBase + '_full_no_color/'

        opts = [
            "--similarity_full", fullSimDataFile,
            "--names", "layout",
            "--scores", attsStringsFile,
            "--directory", outDir,
            "--include-singletons",
            "--no_layout_independent_stats",
            "--no_layout_aware_stats"]

        util.removeOldOutFiles(outDir)
        layout.main(opts)
        util.compareActualVsExpectedDir(s, expNoColorDir, outDir)

    def test_full(s):
        outDir = outDirBase + '_full/'

        #opts for compute sparse to create a full spearman
        opts = [
            '--in_file', rawDataFile,
            '--metric', 'spearman',
            '--output_type', 'full',
            '--out_file', fullSimDataFile,
            '--num_jobs', '2'
        ]

        compute_sparse_matrix.main(opts)

        #options for different layout.py executions
        opts = [
            "--similarity_full", fullSimDataFile,
            "--names", "layout",
            "--scores", attsCodedFile,
            "--colormaps", colorDataFile,
            "--directory", outDir,
            "--include-singletons",
            "--no_layout_independent_stats",
            "--no_layout_aware_stats"]

        util.removeOldOutFiles(outDir)
        layout.main(opts)
        util.compareActualVsExpectedDir(s, expDir, outDir)

    def test_raw_no_atts(s):
        outDir = outDirBase + '_raw_no_atts/'

        opts = [
            "--feature_space", rawDataFile,
            "--names", "layout",
            "--metric", 'spearman',
            "--directory", outDir,
            "--include-singletons",
            "--no_layout_independent_stats",
            "--no_layout_aware_stats"]

        util.removeOldOutFiles(outDir)
        layout.main(opts)
        util.compareActualVsExpectedDir(s, expNoAttsDir, outDir)

    def test_raw_no_color(s):
        outDir = outDirBase + '_raw_no_color/'

        opts = [
            "--feature_space", rawDataFile,
            "--names", "layout",
            "--metric", 'spearman',
            "--scores", attsStringsFile,
            "--directory", outDir,
            "--include-singletons",
            "--no_layout_independent_stats",
            "--no_layout_aware_stats"]

        util.removeOldOutFiles(outDir)
        layout.main(opts)
        util.compareActualVsExpectedDir(s, expNoColorDir, outDir)

    def test_raw(s):
        outDir = outDirBase + '_raw/'

        opts = [
            "--feature_space", rawDataFile,
            "--names", "layout",
            "--metric", 'spearman',
            "--scores", attsCodedFile,
            "--colormaps", colorDataFile,
            "--directory", outDir,
            "--include-singletons",
            "--no_layout_independent_stats",
            "--no_layout_aware_stats"]

        util.removeOldOutFiles(outDir)
        layout.main(opts)
        util.compareActualVsExpectedDir(s, expDir, outDir)

    def test_top6_no_atts(s):
        outDir = outDirBase + '_top6_no_atts/'

        opts = [
            "--similarity", top6SimDataFile,
            "--names", "layout",
            "--directory", outDir,
            "--include-singletons",
            "--no_layout_independent_stats",
            "--no_layout_aware_stats"]

        util.removeOldOutFiles(outDir)
        layout.main(opts)
        util.compareActualVsExpectedDir(s, expNoAttsDir, outDir)

    def test_top6_no_color(s):
        outDir = outDirBase + '_top6_no_color/'

        opts = [
            "--scores", attsStringsFile,
            "--similarity", top6SimDataFile,
            "--names", "layout",
            "--directory", outDir,
            "--include-singletons",
            "--no_layout_independent_stats",
            "--no_layout_aware_stats"]

        util.removeOldOutFiles(outDir)
        layout.main(opts)
        util.compareActualVsExpectedDir(s, expNoColorDir, outDir)

    def test_top6(s):
        outDir = outDirBase + '_top6/'

        opts = [
            "--similarity", top6SimDataFile,
            "--names", "layout",
            "--scores", attsCodedFile,
            "--colormaps", colorDataFile,
            "--directory", outDir,
            "--include-singletons",
            "--no_layout_independent_stats",
            "--no_layout_aware_stats"]

        util.removeOldOutFiles(outDir)
        layout.main(opts)
        util.compareActualVsExpectedDir(s, expDir, outDir)

    def test_xy_no_atts(s):
        outDir = outDirBase + '_xy_no_atts/'

        opts = [
            "--coordinates", coordDataFile,
            "--names", "layout",
            "--directory", outDir,
            "--include-singletons",
            "--no_layout_independent_stats",
            "--no_layout_aware_stats"]

        util.removeOldOutFiles(outDir)
        layout.main(opts)
        util.compareActualVsExpectedDir(s, expNoAttsDir, outDir,
                                        excludeFiles = ['log',
                                                        'neighbors_0.tab',
                                                        'assignments0.tab',
                                                        'hexNames.tab',
                                                        'xyPreSquiggle_0.tab']
                                        )
        util.compareActualVsExpectedFile(s,'neighbors_0.tab',expXyDir,outDir)
        util.compareActualVsExpectedFile(s,'assignments0.tab',expXyDir,outDir)
        util.compareActualVsExpectedFile(s,'xyPreSquiggle_0.tab',expXyDir,outDir)

    def test_xy_no_color(s):
        outDir = outDirBase + '_xy_no_color/'

        opts = [
            "--coordinates", coordDataFile,
            "--scores", attsStringsFile,
            "--names", "layout",
            "--directory", outDir,
            "--include-singletons",
            "--no_layout_independent_stats",
            "--no_layout_aware_stats"]

        util.removeOldOutFiles(outDir)

        layout.main(opts)
        #check that it is mostly the same as the other files
        util.compareActualVsExpectedDir(s, expNoColorDir, outDir,
                                        excludeFiles = ['log',
                                                        'neighbors_0.tab',
                                                        'assignments0.tab',
                                                        'hexNames.tab',
                                                        'xyPreSquiggle_0.tab']
                                        )
        #theese files are not expected to be the same as other runs,
        # but to make sure they are correct we have but previous runs in a different
        # expected directory.
        util.compareActualVsExpectedFile(s,'neighbors_0.tab',expXyDir,outDir)
        util.compareActualVsExpectedFile(s,'assignments0.tab',expXyDir,outDir)
        util.compareActualVsExpectedFile(s,'xyPreSquiggle_0.tab',expXyDir,outDir)

    def test_xy(s):
        outDir = outDirBase + '_xy/'

        opts = [
            "--coordinates", coordDataFile,
            "--names", "layout",
            "--metric", 'spearman',
            "--scores", attsCodedFile,
            "--colormaps", colorDataFile,
            "--directory", outDir,
            "--include-singletons",
            "--no_layout_independent_stats",
            "--no_layout_aware_stats"]

        util.removeOldOutFiles(outDir)

        layout.main(opts)
        #check that it is mostly the same as the other files
        util.compareActualVsExpectedDir(s,expDir, outDir,
                                        excludeFiles = ['log',
                                                        'neighbors_0.tab',
                                                        'assignments0.tab',
                                                        'hexNames.tab',
                                                        'xyPreSquiggle_0.tab']
                                        )
        util.compareActualVsExpectedFile(s,'neighbors_0.tab',expXyDir,outDir)
        util.compareActualVsExpectedFile(s,'assignments0.tab',expXyDir,outDir)
        util.compareActualVsExpectedFile(s,'xyPreSquiggle_0.tab',expXyDir,outDir)

if __name__ == '__main__':
    unittest.main()
