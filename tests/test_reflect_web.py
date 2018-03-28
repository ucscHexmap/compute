#!/usr/bin/env python2.7

import unittest
import reflect_web as test
import  numpy as np
from testUtil import message
from util_web import ErrorResp

class Test_reflect_web(unittest.TestCase):

    reflectMetaDataSchema = {
        "test":
            {
              "dataTypesToCalcType": {
                            "mRNA": "ttest",
                            "CNV" : "average",
                            "miRNA" : "ttest",
                            "RPPA" : "ttest",
                            "Methylation": "ttest"
                           },
              "dataTypesToFileName": {
                            "mRNA": "mRNA.hdf",
                            "CNV" : "CNV.hdf",
                            "miRNA" : "miRNA.hdf",
                            "RPPA" : "RPPA.hdf",
                            "Methylation": "Methylation.hdf"
                           },
              "SampleMap" : {
                  "toMapIds": ["test/GeneMap"],
                  "featOrSamp" : "sample"
              },
              "GeneMap" : {
               "toMapIds" : ["test/SampleMap"],
                "featOrSamp" : "feature"
              }
            }
    }

    def test_getMetaDataWhenMapNotThere(self):
        """Error Response should be raised when mapId is not present."""
        try:
            test.getReflectionMetadata("*notThere*")
        except ErrorResp:
            passes = True

        self.assertTrue(
            passes,
            "No error response thrown when accessing a bad map."
        )

    def test_getDataTypes(self):
        answers = ["mRNA", "CNV", "miRNA", "RPPA", "Methylation"]
        unaligned = test.getDataTypes(
            "test",
            self.reflectMetaDataSchema
        )

        attempt, correct = sorted(unaligned), sorted(answers)

        self.assertTrue(
            np.array_equal(attempt, correct),
            message(attempt, correct)
        )

    def test_getCalcType(self):
        majorId = "test"
        dataType = "mRNA"
        correct = "ttest"
        attempt = test.getCalcType(
            majorId,
            dataType,
            self.reflectMetaDataSchema
        )

        self.assertTrue(
            attempt == correct,
            message(attempt, correct)
        )

    def test_getToMapIds(self):
        mapId = "test/SampleMap"
        correct = ["test/GeneMap"]
        attempt = test.getToMapIds(mapId, self.reflectMetaDataSchema)

        self.assertTrue(
            np.array_equal(attempt, correct),
            message(attempt, correct)
        )

if __name__ == '__main__':
    unittest.main()
