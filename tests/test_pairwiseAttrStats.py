import unittest
import pairwiseAttrStats as stats
import numpy as np

class Test_pairwiseStats(unittest.TestCase):

    binData = np.concatenate(
        [np.repeat(0, 201),
         np.repeat(1, 194)],
        axis=0
    )
    catData = np.concatenate(
        [np.repeat(0, 60),
         np.repeat(1, 54),
         np.repeat(2, 46),
         np.repeat(3, 41),
         np.repeat(0, 40),
         np.repeat(1, 44),
         np.repeat(2, 53),
         np.repeat(3, 57),
         ],
        axis=0
    )

    def test_contingency_table(self):
        """Generate a contingency table and check counts."""
        correct = { (0, 0): 60, (0, 1): 54, (0, 2): 46, (0, 3): 41,
                    (1, 0): 40, (1, 1): 44, (1, 2): 53, (1, 3): 57}

        table = stats.contingencyTable(self.binData, self.catData)
        for indecies in correct.keys():
            self.assertTrue(
                table[indecies] == correct[indecies],
                "indecies: " + str(indecies) + " of contingency table "
                " are incorrect. Actual count is " +
                str(table[indecies]) + " true count is " +
                str(correct[indecies])
            )

    def test_contingency_table_remove_cat(self):
        """Simulates all of one category getting removed."""
        binData = np.concatenate(
            [np.repeat(0, 147),
            np.repeat(1, 150)],
            axis=0
        )
        catData = np.concatenate(
            [np.repeat(0, 60),
             np.repeat(2, 46),
             np.repeat(3, 41),
             np.repeat(0, 40),
             np.repeat(2, 53),
             np.repeat(3, 57),
             ],
            axis=0
          )
        correct = { (0, 0): 60, (0, 1): 46, (0, 2): 41,
                    (1, 0): 40, (1, 1): 53, (1, 2): 57}

        table = stats.contingencyTable(binData, catData)
        for indecies in correct.keys():
            self.assertTrue(
                table[indecies] == correct[indecies],
                "indecies: " + str(indecies) + " of contingency table "
                " are incorrect. Actual count is " +
                str(table[indecies]) + " true count is " +
                str(correct[indecies])
            )

    def test_fliter_na_filter_all(self):
        x = np.repeat(np.NAN, 10)
        y = np.repeat(1, 10)
        x, y = stats.filterNan(x,y)
        self.assertTrue(
            len(x) == len(y) and len(x) == 0,
            "NA filter would not remove all values"
        )

    def test_filter_na_filter_some_from_either(self):
        x = np.concatenate([np.repeat(np.NAN, 3), np.repeat(5, 7)])
        y = np.concatenate([np.repeat(5, 7), np.repeat(np.NAN, 3)])
        x, y = stats.filterNan(x, y)
        self.assertTrue(
            len(x) == len(y) and len(x) == 4,
            "NA filter did not filter properly"
        )

    def test_filter_na_filter_some_from_both(self):
        x = np.concatenate([np.repeat(np.NAN, 3), np.repeat(5, 7)])
        y = np.concatenate([np.repeat(np.NAN, 3), np.repeat(5, 7)])
        x, y = stats.filterNan(x, y)
        self.assertTrue(
            len(x) == len(y) and len(x) == 7,
            "NA filter did not filter properly"
        )

    def test_fisher_exact(self):
        x = np.concatenate([np.repeat(0, 12), np.repeat(1, 12)])
        y = np.concatenate(
            [np.repeat(0, 9),
             np.repeat(1, 3),
             np.repeat(0, 1),
             np.repeat(1, 11)]
        )

        stats.contingencyTable(x,y)
        pvalue = stats.binBinTest(x, y)

        self.assertTrue(
            round(pvalue, 6) == 0.002759,
            "Pvalue didn't come out right: " + str(round(pvalue, 6))
        )

    def test_ranksums(self):
        x = np.array([12, 6, 5, 4, 3, 2])
        y = np.array([11, 10, 9, 8, 7, 1])
        pvalue = stats.contContTest(x, y)

        self.assertTrue(
            round(pvalue, 3) == .095,
            "Pvalue didn't come out right: " + str(round(pvalue, 3))
        )

    def test_binCat_orCatCat(self):
        pvalue = stats.catBinOrCatCatTest(self.binData, self.catData)

        self.assertTrue(
            round(pvalue, 3) == .046,
            "Pvalue didn't come out right: " + str(round(pvalue, 3))
        )


if __name__ == '__main__':
    unittest.main()
