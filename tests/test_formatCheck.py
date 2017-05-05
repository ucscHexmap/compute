import unittest
import os
import pandas as pd
import formatCheck as fc
testDir = os.getcwd()
inDir = os.path.join(testDir,'in/layout/' )   # The input data
xyDir = os.path.join(testDir,'exp/layoutBasicXy/' )   # The input data

class Test_formatCheck(unittest.TestCase):
    """Tests the internal functions of the 'formatCheck' module"""

    # load the pandas data frames into memory.
    full_sim = pd.read_table(os.path.join(inDir, "similarity_full.tab"),
                              index_col =0)
    neighbors = pd.read_table(os.path.join(inDir, "similarity.tab"),
                               index_col =0)
    clusterData = pd.read_table(os.path.join(inDir, "full_matrix.tab"),
                                index_col =0)
    xy1 = pd.read_table(os.path.join(xyDir, "xyPreSquiggle_0.tab"),
                        index_col =0)
    xy2 = pd.read_table(os.path.join(xyDir, "assignments0.tab"),
                        index_col =0)
    unknown = pd.read_table(os.path.join(inDir, "attributes.tab"),
                            index_col =0)

    def test_isXYpositions1(s):
        s.assertTrue(fc._isXYPositions(s.xy1))

    def test_fSimNotXYpositions1(s):
        s.assertTrue(not fc._isXYPositions(s.full_sim))

    def test_sSimNotXYpositions1(s):
        s.assertTrue(not fc._isXYPositions(s.neighbors))

    def test_cDataNotXYpositions1(s):
        s.assertTrue(not fc._isXYPositions(s.clusterData))

    def test_unkownNotXYpositions1(s):
        s.assertTrue(not fc._isXYPositions(s.unknown))

    def test_isXYpositions2(s):
        s.assertTrue(fc._isXYPositions(s.xy2))

    def test_isFullSimilarity(s):
        s.assertTrue(fc._isFullSimilarity(s.full_sim))

    def test_xyNotFullSimilarity(s):
        s.assertTrue(not fc._isFullSimilarity(s.xy1))

    def test_cDataNotFullSimilarity(s):
        s.assertTrue(not fc._isFullSimilarity(s.clusterData))

    def test_sSimNotFullSimilarity(s):
        s.assertTrue(not fc._isFullSimilarity(s.neighbors))

    def test_unknownNotFullSimilarity(s):
        s.assertTrue(not fc._isFullSimilarity(s.unknown))

    def test_isSparseSimilarity(s):
        s.assertTrue(fc._isSparseSimilarity(s.neighbors))

    def test_fSimNotSparseSimilarity(s):
        s.assertTrue(not fc._isSparseSimilarity(s.full_sim))

    def test_cDataNotSparseSimilarity(s):
        s.assertTrue(not fc._isSparseSimilarity(s.clusterData))

    def test_xyNotSparseSimilarity(s):
        s.assertTrue(not fc._isSparseSimilarity(s.xy1))
        s.assertTrue(not fc._isSparseSimilarity(s.xy2))

    def test_unkownNotSparseSimilarity(s):
        s.assertTrue(not fc._isSparseSimilarity(s.unknown))

    def test_isClusterData(s):
        s.assertTrue(fc._isClusterData(s.clusterData))


    def test_sSimNotClusterData(s):
        s.assertTrue(not fc._isClusterData(s.neighbors))


    def test_unknownNotClusterData(s):
        s.assertTrue(not fc._isClusterData(s.unknown))

    def test_inferred_ClusterData(s):
        s.assertTrue(fc._layoutInputFormat(s.clusterData) == "clusterData")

    def test_inferred_xyPositions1(s):
        s.assertTrue(fc._layoutInputFormat(s.xy1) == "xyPositions")

    def test_inferred_xyPositions2(s):
        s.assertTrue(fc._layoutInputFormat(s.xy2) == "xyPositions")

    def test_inferred_unknown(s):
        s.assertTrue(fc._layoutInputFormat(s.unknown) == "unknown")

    def test_inferred_sparseSimilarity(s):
        s.assertTrue(fc._layoutInputFormat(s.neighbors) == "sparseSimilarity")

    def test_inferred_fullSimilarity(s):
        s.assertTrue(fc._layoutInputFormat(s.full_sim) == "fullSimilarity")


if __name__ == '__main__':
    unittest.main()
