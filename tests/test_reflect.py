#!/usr/bin/env python2.7

import os
import unittest

testDir = os.getcwd()
outDir = os.path.join(testDir, 'out/')  # Path to output data.

import testUtil as tu
from reflection import reflection

class Test_reflect(unittest.TestCase):

    def makeDF(self):
        #make some random data for testing
        ncols=50
        nrows=40
        dataDF = tu.getdf('','random',nrows=nrows,ncols=ncols)
        return dataDF

    def hdfOut(self, dataDF):
        dataHdfFile = os.path.join(outDir, "rand.hdf")
        dataDF.to_hdf(dataHdfFile, "matrix")
        return dataHdfFile

    def test_reflect_mRNA(self):

        dataDF = self.makeDF()
        dataHdfFile = self.hdfOut(dataDF)

        parms = {
                "datapath": dataHdfFile,
                "calcType" : "ttest",
                "nodeIds" : dataDF.index[1:10],
                "featOrSamp" : "feature",
                "rankCategories" : True,
                "n" : 10,
                }

        values, nNodes = reflection(parms)

        passed = len(values) == 50 and nNodes == len(parms["nodeIds"])

        self.assertTrue(passed,'reflection call with parms' + str(
            parms) + "\n wasnt the correct length")

    def test_reflect_meth_sample(self):

        dataDF = self.makeDF()
        dataHdfFile = self.hdfOut(dataDF)

        parms = {
                "datapath": dataHdfFile,
                "calcType" : "average",
                "nodeIds" : dataDF.columns[1:10],
                "featOrSamp" : "sample",
                "rankCategories" : True,
                "n" : 10,
                }
        values, nNodes = reflection(parms)

        passed = len(values) == 40 and nNodes == len(parms["nodeIds"])

        self.assertTrue(passed,'reflection call with parms' + str(
            parms) + "\n wasnt the correct length")

    def test_reflect_CNV_sample(self):

        dataDF = self.makeDF()
        dataHdfFile = self.hdfOut(dataDF)

        parms = {
                "datapath": dataHdfFile,
                "calcType" : "average",
                "nodeIds" : dataDF.columns[1:10],
                "featOrSamp" : "sample",
                "rankCategories" : True,
                "n" : 10,
                }
        values, nNodes = reflection(parms)

        passed = len(values) == 40 and nNodes == len(parms["nodeIds"])

        self.assertTrue(passed,'reflection call with parms' + str(
            parms) + "\n wasnt the correct length")


if __name__ == '__main__':
    unittest.main()
