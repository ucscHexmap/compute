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

    def test_map_meta_json(s):
        outDir = os.path.join(outDirBase, 'mapMetaCalc')
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
        util.compareActualVsExpectedFile(s, 'mapMeta.json', expMetaDir, outDir)

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

    def test_group_meta_exists_json_view_group_dir(s):
        outMetaDir = os.path.join(outDirBase, 'groupMetaCalcExistsGroup/view/group')
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
        
        # Make a beginning meta.json to change
        try:
            os.makedirs(outMetaDir)
        except:
            pass
        meta = None
        with open(os.path.join(expMetaDir, 'meta.json'), 'r') as f:
            meta = json.load(f)
        meta['role'] = 'oldRole'
        outMetaFile = os.path.join(outMetaDir, 'meta.json')
        with open(outMetaFile, 'w') as f:
            json.dump(meta, f, indent=4)

        layout.main(opts)
        
        with open(outMetaFile, 'r') as f:
            meta = json.load(f)
        s.assertTrue(meta['role'] == 'oldRole')

if __name__ == '__main__':
    unittest.main()
