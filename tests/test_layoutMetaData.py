import os, shutil, json
import unittest
import layout
import testUtil as util

testDir = os.getcwd()
inDir = os.path.join(testDir, 'in/layout/')
outDirBase = os.path.join(testDir, 'out/')
expMetaDir = os.path.join(testDir, 'exp/meta')

clusterDataFile = os.path.join(inDir, 'full_matrix.tab')

class Layout_calc_meta_tests(unittest.TestCase):

    def test_map_meta_json_standard_group(s):
        inDir = os.path.join(testDir, 'in/dataRoot/featureSpace/groupName/mapName')
        outDir = os.path.join(outDirBase, 'mapMetaCalcStandardGroup')
        opts = [
            "--layoutInputFile", os.path.join(inDir, 'full_matrix.tab'),
            "--layoutInputFile", os.path.join(inDir, 'full_matrix_2.tab'),
            "--layoutInputFormat", 'clusterData',
            "--layoutName", "layout",
            "--layoutName", "layout_2",
            "--outputDirectory", outDir,
            "--noLayoutIndependentStats",
            "--noLayoutAwareStats"]
        util.removeOldOutFiles(outDir)
        layout.main(opts)
        util.compareActualVsExpectedFile2(s,
            os.path.join(expMetaDir, 'mapMetaGroup.json'),
            os.path.join(outDir, 'mapMeta.json'))

    def test_map_meta_json_standard_simple(s):
        inDir = os.path.join(testDir, 'in/dataRoot/featureSpace/simpleMapName')
        outDir = os.path.join(outDirBase, 'mapMetaCalcStandardSimple')
        opts = [
            "--layoutInputFile", os.path.join(inDir, 'full_matrix.tab'),
            "--layoutInputFile", os.path.join(inDir, 'full_matrix_2.tab'),
            "--layoutInputFormat", 'clusterData',
            "--layoutName", "layout",
            "--layoutName", "layout_2",
            "--outputDirectory", outDir,
            "--noLayoutIndependentStats",
            "--noLayoutAwareStats"]
        util.removeOldOutFiles(outDir)
        layout.main(opts)
        util.compareActualVsExpectedFile2(s,
            os.path.join(expMetaDir, 'mapMetaSimple.json'),
            os.path.join(outDir, 'mapMeta.json'))

    def test_map_meta_json_non_standard(s):
        outDir = os.path.join(outDirBase, 'mapMetaCalcNonStandard')
        opts = [
            "--layoutInputFile", os.path.join(inDir, 'full_matrix.tab'),
            "--layoutInputFile", os.path.join(inDir, 'full_matrix_2.tab'),
            "--layoutInputFormat", 'clusterData',
            "--layoutName", "layout",
            "--layoutName", "layout_2",
            "--outputDirectory", outDir,
            "--noLayoutIndependentStats",
            "--noLayoutAwareStats"]
        util.removeOldOutFiles(outDir)
        layout.main(opts)
        util.compareActualVsExpectedFile2(s,
            os.path.join(expMetaDir, 'mapMetaEmpty.json'),
            os.path.join(outDir, 'mapMeta.json'))

    def test_group_meta_json_no_view_dir(s):
        outDir = os.path.join(outDirBase, 'groupMetaCalcNoView')
        opts = [
            "--layoutInputFile", os.path.join(inDir, 'similarity.tab'),
            "--layoutInputFormat", 'sparseSimilarity',
            "--layoutName", "layout",
            "--role", "myRole",
            "--outputDirectory", outDir,
            "--noLayoutIndependentStats",
            "--noLayoutAwareStats"]
        util.removeOldOutFiles(outDir)
        layout.main(opts)
        util.compareActualVsExpectedFile(s, 'meta.json', expMetaDir, outDir)

    def test_group_meta_json_view_no_group_dir(s):
        outDir = os.path.join(outDirBase, 'groupMetaCalcNoGroup/view/baseMap')
        opts = [
            "--layoutInputFile", os.path.join(inDir, 'similarity.tab'),
            "--layoutInputFormat", 'sparseSimilarity',
            "--layoutName", "layout",
            "--role", "myRole",
            "--outputDirectory", outDir,
            "--noLayoutIndependentStats",
            "--noLayoutAwareStats"]
        util.removeOldOutFiles(outDir)
        layout.main(opts)
        util.compareActualVsExpectedFile(s, 'meta.json', expMetaDir, outDir)

    def test_group_meta_json_view_group_dir(s):
        outMetaDir = os.path.join(outDirBase, 'groupMetaCalcGroup/view/group')
        outDir = os.path.join(outMetaDir, 'baseMap')
        opts = [
            "--layoutInputFile", os.path.join(inDir, 'similarity.tab'),
            "--layoutInputFormat", 'sparseSimilarity',
            "--layoutName", "layout",
            "--role", "myRole",
            "--outputDirectory", outDir,
            "--noLayoutIndependentStats",
            "--noLayoutAwareStats"]
        util.removeOldOutFiles(outDir)
        layout.main(opts)
        util.compareActualVsExpectedFile(s, 'meta.json', expMetaDir, outMetaDir)

if __name__ == '__main__':
    unittest.main()
