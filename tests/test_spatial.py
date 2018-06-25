import unittest
import numpy as np
import spatial as test
from testUtil import message

import unittest
import pandas as pd
import numpy as np
import spatial
import mapData
import os

class Test_dynLayoutAware(unittest.TestCase):
    dummy_xys = pd.DataFrame(
        [
            [4,5],
            [5,6],
            [7,8],
            [4,5],
            [5,6],
            [7,8],
            [4,5],
            [5,6],
        ]
    )

    def test_inverse_euc_distance(s):
        euclidean_xys = pd.DataFrame([
            [0, 0],
            [3, 4],
            [5, 12],
        ])

        # Done on a calculator.
        realEucDistance = [
            [0, 5, 13],
            [5, 0, 8.2462],
            [13, 8.2462, 0],
        ]

        answers = 1 / (1 + np.array(realEucDistance))
        calculated = spatial.inverseEucDistance(euclidean_xys)

        allGood = np.allclose(answers, calculated)

        s.assertTrue(
            allGood,
            "actual values:\n" +
            str(answers) +
            "\nwhether the cell is matching:\n" +
            str(np.isclose(answers, calculated)) +
            "\ncalculated values:\n" +
            str(calculated)
        )

    def test_attrPreProcessing_no_na(self):
        attr = pd.Series([1, 1, 1, 1, 0, 0, 0, 0])
        attr = spatial.attrPreProcessing(self.dummy_xys, attr)

        self.assertTrue(
            len(attr) == 8 and attr.loc[6] == -1,
            str(attr)
        )

    def test_attrPreProcessing_with_DF(self):
        attr = pd.DataFrame(
            {
                "A": [1, 1, 1, 1, 0, 0, 0, 0],
                "B": [1, 1, 1, 1, 0, 0, 0, 0]
            }
        )
        attr = spatial.attrPreProcessing(self.dummy_xys, attr)

        self.assertTrue(
            len(attr) == 8 and attr["B"].loc[6] == -1,
            str(attr)
        )

    def test_attrPreProcessing_with_na(self):
        """Check nan value sharing a row with xys is set to 0."""
        attr = pd.Series([1, 1, 1, 1, np.nan, 0, 0, 0])
        attr = spatial.attrPreProcessing(self.dummy_xys, attr)
        self.assertTrue(
            len(attr) == 8 and attr.loc[4] == 0,
            str(attr)
        )

    def test_attrPreProcessing_with_na_value_change(self):
        """Check real value changes with na present."""
        attr = pd.Series([1, 1, 1, 1, np.nan, 0, 0, 0])
        attr = spatial.attrPreProcessing(self.dummy_xys, attr)
        correct = 0.866025
        self.assertTrue(
            len(attr) == 8 and np.isclose(attr.loc[3], correct),
            str(attr.loc[3]) + " |didn't match| " + str(correct)
        )

    def test_oneByAll(self):
        """Tests that 1 by all gives known answers."""
        # [LeesL, Ranks, Pearson R] are the columns of answers.
        answers = np.array([
            [0.120261,  0.416667,  1.000000],
            [-0.005115,  0.833333,  0.532354],
            [0.120261,  0.416667,  1.000000],
            [0.0118875,  0.666667, -0.512821],
            [-0.120261,  0.083333, -1.000000],
            [-0.120261, 0.083333, -1.000000]
        ])
        # mapData class needs these set to work properly.
        os.environ["DATA_ROOT"] = os.path.join(
            os.environ["HEXCALC"],
            "tests/in/dataRoot"
        )

        mapName = "unitTest/layoutBasicExp"

        # Gather Data.
        binAttrs = mapData.getAllBinaryAttrs(mapName)
        firstColumn = binAttrs.columns[0]
        dynAttr = binAttrs[firstColumn]
        real_xys = mapData.getXYs(mapName, 0)

        # Run calculation to test.
        calculated = spatial.oneByAll(binAttrs, dynAttr, real_xys)

        allGood = np.allclose(calculated.values, answers)

        self.assertTrue(
            allGood,
            "actual values:\n" +
            str(answers) +
            "whether the cell is matching:\n" +
            str(np.isclose(answers, calculated.values)) + "\n" +
            "calculated values:\n" +
            str(calculated.values)
        )

    def test_catSSS_2x2(self):
        """Function reproduces known value."""
        example = np.array([
            [1, -1],
            [-1, 1]
        ])

        correct = 2
        attempt = test.catSSS(example)
        self.assertTrue(
            np.isclose(attempt, correct),
            message(attempt, correct)
        )

    def test_catSSS_3x3(self):
        """Function reproduces known value."""
        example = np.array([
            [1, -1, -1],
            [-1, 1, -1],
            [-1, -1, 1],
        ])

        correct = 2
        attempt = test.catSSS(example)
        self.assertTrue(
            np.isclose(attempt, correct),
            message(attempt, correct)
        )

    def test_catSSS_4x4(self):
        """Function reproduces known value."""
        example = np.array([
            [10, -10, -5, -15],
            [-10, 10, -5, -15],
            [-5, -5, 10, -10],
            [-15, -15, -10, 10],
        ])

        correct = 20
        attempt = test.catSSS(example)
        self.assertTrue(
            np.isclose(attempt, correct),
            message(attempt, correct)
        )

if __name__ == '__main__':
    unittest.main()
